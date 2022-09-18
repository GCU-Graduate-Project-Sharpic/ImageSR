import argparse
import os
import sys
import time
from dotenv import load_dotenv

from databases.databases import Databases
import alert


def localhost_info():
    load_dotenv()
    host, dbname = os.environ.get('HOST'), os.environ.get('DATABASE')
    user, password = os.environ.get('USER_SQL'), os.environ.get('PASS')
    port = os.environ.get('PORT')

    print(host, dbname, user, password, port)

    return host, dbname, user, password, port


def backend_info():
    host, dbname = 'sharpic.chromato99.com', 'Sharpic'
    user, password = 'postgres', 'sharpgcu75!@'
    port = 55432

    return host, dbname, user, password, port

"""
def get_argument(argv):
    parser = argparse.ArgumentParser()
    parser_action = parser.add_mutually_exclusive_group(required=True)
    parser_action.add_argument("--store", action='store_const', const=True,
                               help="Load an image from the named file and save it in the DB")
    parser_action.add_argument("--fetch", type=int,
                               help="Fetch an image from the DB and store it in the named file, overwriting it if it "
                                    "exists. Takes the database file identifier as an argument.",
                               metavar='42')
    parser.add_argument("filename", help="Name of file to write to / fetch from")

    arg_lst = parser.parse_args(argv[1:])

    return arg_lst """


def __exceed_user_size_limit(logged_user):
    logged_db = Databases(*localhost_info())
    logged_db.ensure_db()
    img_len = logged_db.get_number_of_images_by_user(logged_user)

    if img_len[0] > 100:
        return True
    else:
        return False


def __no_need_to_be_process(logged_user):
    logged_db = Databases(*localhost_info())
    logged_db.ensure_db()
    user_img_lst = logged_db.load_user_images(logged_user)

    if len(user_img_lst) == 0:
        return True
    else:
        sr_img_lst = logged_db.get_images_which_need_sr_by_user(username=logged_user, down=False)
        if len(sr_img_lst) == 0:
            return True
        return False


if __name__ == '__main__':
    host, db, user, pw, port = localhost_info()

    db = Databases(host, db, user, pw, port)
    print(f'Connection success')

    db.ensure_db()

    DELAY = 3
    while True:
        # load all users
        alert.loop()

        user_list = db.get_distinct_user()
        for username in user_list:
            # User logged in ...

            if __no_need_to_be_process(username):
                continue  # pass processing, go to next user

            user_image_lst = db.load_user_images(username=username)

            # ALERT: Verify if user has more than 100 images
            if __exceed_user_size_limit(username):
                alert.size_exceed_alert(username=username)
            else:
                print(f'User {username}\'s image server is running')
                print(f'User {username} has {100 - len(user_image_lst)} images left')

                print(f'Load {username}\'s lq images...')
                need_sr = db.get_images_which_need_sr_by_user(username=username, down=True)

                # save loaded images into server...

                print(f'User {username} has {len(need_sr)} images which need sr')
                print(f'Load SR method and start SR...')

                # SR method
                os.system('../RealSR/codes/SR_MPS.sh')
                # ...

                # upload Recon images
                print(f'Upload Recon images...')
                db.insert_recon_image(need_sr)

                print(f'SR done')

        # print(f'Waiting {DELAY} seconds')
        time.sleep(DELAY)
