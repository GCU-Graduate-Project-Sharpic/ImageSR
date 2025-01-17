import os
import time
from dotenv import load_dotenv

import databases.databases as db


def backend_info():
    load_dotenv()
    host, dbname = os.environ.get('HOST'), os.environ.get('DATABASE')
    user, password = os.environ.get('USER_SQL'), os.environ.get('PASS')
    port = os.environ.get('PORT')
    minio_host, minio_access_id, minio_access_pw = os.environ.get('MINIO_HOST'), os.environ.get('MINIO_ACCESS_ID'), os.environ.get('MINIO_ACCESS_PW')

    print(host, dbname, user, password, port, minio_host, minio_access_id, minio_access_pw)

    return host, dbname, user, password, port, minio_host, minio_access_id, minio_access_pw


if __name__ == '__main__':

    db_handler = db.Databases(*backend_info())
    db_handler.init_db(force_init=False)

    # initial clear
    db_handler.clear_local()

    # loop every 5 seconds
    while True:
        process_list = db_handler.glance_db()
        print(f"Number of unprocessed images: {len(process_list)}")

        if len(process_list) == 0:
            print("No process to be done")
        else:
            db_handler.process_db(process_list)
            db_handler.clear_local()
        time.sleep(5)
