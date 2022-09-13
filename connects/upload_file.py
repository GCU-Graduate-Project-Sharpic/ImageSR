import os

from databases.databases import Databases

def localhost_info():
    host, dbname = '192.168.35.38', 'Sharpic'
    user, password = 'postgres', 'secret'
    port = 5432

    return [host, dbname, user, password, port]

def backend_info():
    host, dbname = 'sharpic.chromato99.com', 'Sharpic'
    user, password = 'postgres', 'sharpgcu75!@'
    port = 55432

    return host, dbname, user, password, port


def read_filename_in_folder():
    img_lst = []
    for file in os.listdir('./LR_VL'):
        if file.endswith('.png'):
            img_lst.append(file)
    return img_lst


def upload_all():
    logged_db = Databases(*localhost_info())
    logged_db.ensure_db()
    img_lst = read_filename_in_folder()

    i = 0

    for non_sr_image_name in img_lst:
        with open(f'./LR_VL/{non_sr_image_name}', 'rb') as f:
            i += 1
            img_file = f.read()
            if i % 7 == 0: logged_db.upload('Cho', f'./LR_VL/{non_sr_image_name}', False)
            elif i % 5 == 0: logged_db.upload('Kim', f'./LR_VL/{non_sr_image_name}', False)
            elif i % 3 == 0: logged_db.upload('Hyun', f'./LR_VL/{non_sr_image_name}', False)
            else: logged_db.upload('Kang', f'./LR_VL/{non_sr_image_name}', False)


if __name__ == '__main__':
    host, db, user, pw, port = localhost_info()

    db = Databases(host, db, user, pw, port)
    db.delete_all_from_table()
    upload_all()