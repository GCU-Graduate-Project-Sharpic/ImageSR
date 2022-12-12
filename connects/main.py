import os
import time
from dotenv import load_dotenv

import databases.databases as db


def backend_info():
    load_dotenv()
    host, dbname = os.environ.get('HOST_RAS'), os.environ.get('DATABASE_RAS')
    user, password = os.environ.get('USER_SQL_RAS'), os.environ.get('PASS_RAS')
    port = os.environ.get('PORT_RAS')

    print(host, dbname, user, password, port)

    return host, dbname, user, password, port


if __name__ == '__main__':

    db_handler = db.Databases(*backend_info())
    db_handler.init_db(force_init=False)

    # initial clear
    db_handler.clear_local()

    # loop every 5 seconds
    while True:
        process_list, n_process = db_handler.glance_db()
        print(f"Number of unprocessed images: {n_process}")

        if n_process == 0:
            print("No process to be done")
        else:
            db_handler.process_db(process_list)
            db_handler.clear_local()
        time.sleep(5)
