import psycopg2
import os

import torch.cuda


def _change_ext(image_name):
    if image_name.endswith('.jpg'):
        image_name = image_name[:-4] + '.png'
    elif image_name.endswith('.jpeg'):
        image_name = image_name[:-5] + '.png'
    return image_name


class Databases:
    def __init__(self, host, dbname, user, pw, port):
        self.conn = psycopg2.connect(host=host, dbname=dbname, user=user, password=pw, port=port)
        self.curs = self.conn.cursor()
        self.table_scheme = """
            CREATE TABLE image (id SERIAL PRIMARY KEY, 
                                username VARCHAR(30) NOT NULL , 
                                image_name VARCHAR(100) NOT NULL, 
                                image_file bytea NOT NULL , 
                                size INT NOT NULL , 
                                
                                up int NOT NULL
            )
            """
        print("DB connected")

    """
    Initialize the database
    _check_table() checks if the table exists
    _create_table() creates the table
    _drop_table() drops the table
    
    init_db() is called in main.py
    """
    def _check_table(self):
        self.curs.execute("SELECT EXISTS(SELECT * FROM information_schema.tables WHERE table_name=%s)", ('image',))
        if not self.curs.fetchone()[0]:
            self._create_table()
        else:
            print("Table exists")

    def _create_table(self):
        self.curs.execute(self.table_scheme)
        self.conn.commit()
        print("Table created")

    def _drop_table(self):
        self.curs.execute("DROP TABLE image")
        self.conn.commit()
        print("Table dropped")

    def init_db(self, force_init=False):
        if force_init:
            self._drop_table()
        self._check_table()

    """
    Check if there are any image that are not processed
    _check_unprocessed() checks if there are any unprocessed images, and return their's image_name as a list
    _check_pair() checks if there is a pair of images (LQ and SR) for the unprocessed image
    
    glance_db() is called in main.py
    """
    def _check_unprocessed(self):
        """
        TODO: check up type
        """
        self.curs.execute("SELECT image_name FROM image WHERE up != -1")
        unprocessed = self.curs.fetchall()
        unprocessed = [i[0] for i in unprocessed]
        # print("Unprocessed images: ", unprocessed)
        return unprocessed

    def _check_pair(self, unprocessed):
        processed = []
        for i in unprocessed:
            self.curs.execute("SELECT image_name FROM processed_image WHERE image_name = %s", (i,))
            if self.curs.fetchone():

                """
                check if the pair (same image_name, same up) exists
                """
                self.curs.execute("SELECT up FROM image WHERE image_name = %s", (i,))
                up = self.curs.fetchone()[0]
                self.curs.execute("SELECT up FROM processed_image WHERE image_name = %s", (i,))
                pr_up = self.curs.fetchone()[0]

                if up == pr_up:
                    processed.append(i)

        need_process = list(set(unprocessed) - set(processed))
        return need_process

    def glance_db(self):
        unprocessed = self._check_unprocessed()
        need_process = self._check_pair(unprocessed)
        return need_process, len(need_process)

    """
    Process the image
    _check_type() checks what types of service the image needs
    _download() downloads the image from the database
    _upload() uploads the processed image to the database
    
    process_db() is called in main.py
    """
    def _check_type(self, image_name):
        self.curs.execute("SELECT up FROM image WHERE image_name = %s", (image_name,))
        up = self.curs.fetchone()[0]
        return up

    def _download(self, image_name):
        self.curs.execute("SELECT id, image_file, username FROM image WHERE image_name = %s", (image_name,))
        (npr_id, image_file, user_name) = self.curs.fetchone()
        pr_type = self._check_type(image_name)

        # make int to str
        pr_type = str(pr_type)

        image_name = _change_ext(image_name)
        path = './LQ/' + pr_type + '/' + image_name
        f = open(path, 'wb')
        f.write(image_file)
        f.close()
        print("Fetched {0} into path {1} | Owner: {2}".format(image_name, path, user_name))

    def _upload(self, image_name, id, username):
        pr_type = self._check_type(image_name)
        png_image_name = _change_ext(image_name)
        if pr_type == -1:
            return
        elif pr_type == 0:
            path = '../RealSR/results/Sharpic-SR/DIV2K/' + png_image_name
        elif pr_type == 1:
            path = '../BOPB/result/old/final_output/' + png_image_name
        elif pr_type == 2:
            path = '../BOPB/result/old_w_scratch/final_output/' + png_image_name
        elif pr_type == 3:
            path = '../waifu2x/results/' + png_image_name
        else:
            raise ValueError("Error: up value is not 0, 1, 2 or 3")

        assert os.path.exists(path), "Error: path does not exist"
        file_size = os.path.getsize(path)
        f = open(path, 'rb')

        file_data = f.read()
        id = id[1]

        print(id)
        print(username)

        # insert
        up = self._check_type(image_name)
        self.curs.execute("INSERT INTO processed_image(id, username, image_name, image_file, size, up) VALUES (%s, %s, %s, %s, %s, %s) RETURNING id",
                          (id, username, image_name, file_data, int(file_size), up))
        self.conn.commit()
        f.close()
        print("Stored {0} into DB".format(image_name))

    def process_db(self, image_list):

        npr_id_lst = []
        for image in image_list:
            # pass
            npr_id_lst.append(self._download(image))

        import os
        # get name of all files in the directory
        if len(os.listdir('./LQ/0/')) != 0:
            print("SR processing does not support CPU")
            print("ONLY support CUDA or MPS")
            if torch.cuda.is_available():
                print("Using GPU")
                os.system("../RealSR/codes/SR_CUDA.sh")
            else:
                print("Using MPS")
                os.system('../RealSR/codes/SR_MPS.sh')

        if len(os.listdir('./LQ/1/')) != 0:
            # change directory using os.chdir()
            os.chdir('../BOPB/')
            os.system('./runner/img_wo_scratches.sh')
            os.chdir('../connects/')

        if len(os.listdir('./LQ/2/')) != 0:
            os.chdir('../BOPB/')
            os.system('../BOPB/runner/img_w_scratches.sh')
            os.chdir('../connects/')

        if len(os.listdir('./LQ/3/')) != 0:
            os.chdir('../waifu2x/script_generator/')
            os.system('python load_scr_and_run.py')
            os.chdir('../../connects/')

        id_lst = self._get_image_id(image_list)
        pr, npr, npr_user = id_lst[0], id_lst[1], id_lst[2]

        for idx, image in enumerate(image_list):
            self._upload(image, npr[idx], npr_user[idx])

        print("Finished processing")
        # self.update_album(self._get_album_id(self._get_image_id(image_list)))

    """
    Clear the local directory
    1. Delete all files in the directory
    """
    def clear_local(self):
        print("Clearing local directory ... ")
        for file in os.listdir('./LQ/0/'):
            os.remove('./LQ/0/' + file)
        for file in os.listdir('./LQ/1/'):
            os.remove('./LQ/1/' + file)
        for file in os.listdir('./LQ/2/'):
            os.remove('./LQ/2/' + file)
        for file in os.listdir('./LQ/3/'):
            os.remove('./LQ/3/' + file)
        for file in os.listdir('../RealSR/results/Sharpic-SR/DIV2K/'):
            os.remove('../RealSR/results/Sharpic-SR/DIV2K/' + file)
        for file in os.listdir('../BOPB/result/old/final_output/'):
            os.remove('../BOPB/result/old/final_output/' + file)
        for file in os.listdir('../BOPB/result/old_w_scratch/final_output/'):
            os.remove('../BOPB/result/old_w_scratch/final_output/' + file)
        for file in os.listdir('../waifu2x/results/'):
            os.remove('../waifu2x/results/' + file)

    """
    Update album
    1. processing 이 필요한 사진 list 들이 존재한다. 
    2. 이 때 album_table 에서 해당 사진들(= image_id 로 판별한다.) 의 album_id 를 가져 온다.
    3. 이후 processing 된 사진들을 album_table 에 insert 한다. 
    
    """
    def _get_image_id(self, need_process, processed: bool = False):
        processed_img_id_lst = []
        unprocessed_img_id_lst = []
        unprocessed_user_lst = []

        if processed:
            for img in need_process:
                self.curs.execute("SELECT id FROM processed_image WHERE image_name = %s", (img,))
                processed_img_id_lst.append([img, self.curs.fetchone()[0]])

        for img in need_process:
            # get id, username where image_name = img
            self.curs.execute("SELECT id, username FROM image WHERE image_name = %s", (img,))
            (temp_id, temp_user) = self.curs.fetchone()
            unprocessed_img_id_lst.append([img, temp_id])
            unprocessed_user_lst.append(temp_user)

        return [processed_img_id_lst, unprocessed_img_id_lst, unprocessed_user_lst]  # [[image_name, image_id]]

    def _get_album_id(self, lst):  # img_id_lst = [[image_name, image_id]]
        processed, not_processed = lst[0], lst[1]
        album_id_lst = []

        for img in not_processed:
            self.curs.execute("SELECT album_id FROM album_image WHERE image_id = %s", (img[1],))
            album_id_lst.append(self.curs.fetchone()[0])

        return album_id_lst  # [[image_name, image_id], album_id]

    def update_album(self, album_id_lst):
        for album in album_id_lst:
            image_name = album[0][0]
            image_id = album[0][1]
            album_id = album[1]

            print("image_name: {0}, image_id: {1}, album_id: {2}".format(image_name, image_id, album_id))

            self.curs.execute("INSERT INTO album_image(album_id, image_id) VALUES (%s, %s)",
                              (album_id, image_id))
            self.conn.commit()

        print("Finished updating album")
