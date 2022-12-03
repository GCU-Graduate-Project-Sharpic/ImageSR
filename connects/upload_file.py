import databases.databases as db


def localhost_info():
    host, dbname = 'localhost', 'postgres'
    user, password = 'postgres', 'Carpe06*'
    port = 5432

    return host, dbname, user, password, port


if __name__ == '__main__':

    db_handler = db.Databases(*localhost_info())
    db_handler.init_db(force_init=False)

    import os
    sample_lq_image_root_path = './lq_for_init/'

    # retrieve all the image name
    image_name_list = os.listdir(sample_lq_image_root_path)

    # sample user
    users = ['user1', 'user2', 'user3', 'user4', 'user5']

    # insert into db randomly
    import random
    for image_name in image_name_list:
        user = users[random.randint(0, 4)]
        db_handler.upload_sample_lq(sample_lq_image_root_path, image_name, user)

    print("Done")
