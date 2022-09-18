import psycopg2
import os


class Databases:

    def __init__(self, host, dbname, user, pw, port):
        self.conn = psycopg2.connect(host=host, dbname=dbname, user=user, password=pw, port=port)
        self.curs = self.conn.cursor()
        self.create_table_stm = """
            CREATE TABLE images (
                id serial primary key,
                username text not null ,
                image_name text not null,
                image_file bytea not null,
                size integer not null,
                sr BOOLEAN not null
            )
            """

    def ensure_db(self):
        self.curs.execute("SELECT 1 FROM information_schema.tables WHERE table_schema = %s AND table_name = %s",
                          ('public', 'images'))

        result = self.curs.fetchall()
        if len(result) == 0:
            print('Create DB..')
            self.curs.execute(self.create_table_stm)

    def load_all(self):
        self.curs.execute("SELECT image_name, username, sr FROM images")
        img_lst = self.curs.fetchall()

        return img_lst

    def get_number_of_images_by_user(self, username):
        self.curs.execute("SELECT COUNT(*) FROM images WHERE username = %s", (username,))
        img_len = self.curs.fetchone()

        return img_len

    def get_user_who_more_than_100(self):
        self.curs.execute("SELECT username, COUNT(*) FROM images GROUP BY username HAVING COUNT(*) > 100")
        img_len = self.curs.fetchall()

        return img_len

    def load_user_images(self, username):
        self.curs.execute("SELECT image_name, username, sr FROM images WHERE username = %s", (username,))
        user_img_lst = self.curs.fetchall()

        return user_img_lst

    def is_user_more_than_100(self, username):
        self.curs.execute("SELECT COUNT(*) FROM images WHERE username = %s", (username,))
        img_len = self.curs.fetchone()

        if img_len[0] > 100:
            return True
        else:
            return False

    def get_distinct_user(self):
        self.curs.execute("SELECT DISTINCT username FROM images")
        user_lst = self.curs.fetchall()

        return user_lst

    def get_username_list(self):
        self.curs.execute("SELECT DISTINCT username FROM images")
        username_lst = self.curs.fetchall()

        return username_lst

    def get_images_which_need_sr_by_user(self, username, down=False):
        already_sr = self.get_sr_true_image_by_user(username)
        self.curs.execute("SELECT image_name, username, sr, id FROM images WHERE username = %s AND sr = FALSE", (username,))
        img_lst = self.curs.fetchall()

        for idx, img in enumerate(already_sr):
            if img[0] == img_lst[idx][0]:
                img_lst.pop(idx)

        # save images
        if down:
            for img in img_lst:
                self.download(img[0], img[3])

        return img_lst

    def download(self, filename, fetch_id):
        filename = filename.split('/')[-1]
        path = './LQ/' + filename
        f = open(path, 'wb')
        self.curs.execute("SELECT image_file, image_name, username FROM images WHERE id = %s", (int(fetch_id),))
        (image_file, image_name, user_name) = self.curs.fetchone()

        f.write(image_file)
        f.close()
        print("Fetched {0} into file {1}; original filename was {2} | Owner: {3}".format(fetch_id, filename, image_name, user_name))

        return image_name, user_name

    def get_sr_true_image_by_user(self, username):
        self.curs.execute("SELECT image_name, username, sr FROM images WHERE username = %s AND sr = TRUE", (username,))
        img_lst = self.curs.fetchall()

        return img_lst

    def load_non_sr(self):
        self.curs.execute("SELECT image_name, username, sr FROM images WHERE sr = FALSE")
        none_sr_img_lst = self.curs.fetchall()

        return none_sr_img_lst

    def insert_recon_image(self, image_lst):
        for img in image_lst:
            self.upload(img[1], img[0], True)

    def upload(self, username, filename, is_sr):
        filename = filename.split('/')[-1]
        path = '../RealSR/results/Sharpic-SR/DIV2K/' + filename

        file_size = os.path.getsize(path)
        user_name = username

        f = open(path, 'rb')
        file_data = f.read()
        self.curs.execute("INSERT INTO images(id, username, image_name, image_file, size, sr) VALUES (DEFAULT, %s, %s, %s, %s, %s) RETURNING id",
                          (user_name, filename, file_data, int(file_size), is_sr))

        returned_id = self.curs.fetchone()[0]
        f.close()
        self.conn.commit()
        print("Stored {0} into DB record {1}".format(filename, returned_id))

    def delete_all_from_table(self):
        self.curs.execute("DELETE FROM images")
        print('DELETE ALL')

    def discon(self):
        self.conn.close()

    def delete_image_by_id(self, id):
        self.curs.execute("DELETE FROM images WHERE id=%s;", (id,))
        print(f'DELETE file: {id}')

    def get_len(self):
        self.curs.execute("SELECT COUNT(*) FROM images")
        img_len = self.curs.fetchone()

        return img_len
