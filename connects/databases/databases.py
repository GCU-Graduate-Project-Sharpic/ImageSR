import psycopg2
import os
import time
import torch.cuda
import hashlib
from minio import Minio
from minio.error import S3Error

class Databases:
    def __init__(self, host, dbname, user, pw, port, minio_host, minio_access_id, minio_access_pw):

        # Waiting db initialization
        start_time = time.time()
        while (time.time() - start_time) < 15 :
            try: 
                self.conn = psycopg2.connect(host=host, dbname=dbname, user=user, password=pw, port=port)
                self.curs = self.conn.cursor()
                self.table_scheme = """
                    CREATE TABLE image (
                        id SERIAL PRIMARY KEY,
                        username VARCHAR(30) REFERENCES user_account,
                        image_name VARCHAR(100) NOT NULL,
                        image_hash CHAR(64) NOT NULL,
                        size int NOT NULL,
                        added_date timestamp DEFAULT Now(),
                        up int NOT NULL
                    )
                    """
                print("DB connected")
                
                self.minioClient = Minio(
                    minio_host,
                    access_key=minio_access_id,
                    secret_key=minio_access_pw,
                    secure=False,
                )

                # check bucket.
                found = self.minioClient.bucket_exists("images")
                if not found:
                    raise S3Error(f"bucket does not exist")
                break
            except psycopg2.OperationalError as e:
                print(e)
                print("Waiting DB connection...")
            time.sleep(1)

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
        self.curs.execute("SELECT id FROM image WHERE up != -1 AND NOT EXISTS (SELECT 1 FROM processed_image WHERE id=image.id)")
        unprocessed = self.curs.fetchall()
        unprocessed = [i[0] for i in unprocessed]
        # print("Unprocessed images: ", unprocessed)
        return unprocessed

    def _check_pair(self, unprocessed):
        processed = []
        for i in unprocessed:
            self.curs.execute("SELECT up FROM processed_image WHERE id = %s", (i,))
            if self.curs.fetchone():

                """
                check if the pair (same id, same up) exists
                """
                self.curs.execute("SELECT up FROM image WHERE id = %s", (i,))
                up = self.curs.fetchone()[0]
                self.curs.execute("SELECT up FROM processed_image WHERE id = %s", (i,))
                pr_up = self.curs.fetchone()[0]

                if up == pr_up:
                    processed.append(i)

        need_process = list(set(unprocessed) - set(processed))
        return need_process

    def glance_db(self):
        unprocessed = self._check_unprocessed()
        # need_process = self._check_pair(unprocessed)
        return unprocessed

    """
    Process the image
    _download() downloads the image from the database
    _upload() uploads the processed image to the database
    
    process_db() is called in main.py
    """
    def _download(self, image_id):
        image = {'id': image_id}
        self.curs.execute("SELECT username, image_name, image_hash, up FROM image WHERE id = %s", (image_id,))
        (image['username'], image['image_name'], image['image_hash'], image['pr_type']) = self.curs.fetchone()

        image['image_file'] = self.minioClient.get_object("images", image['image_hash']).read()

        path = './LQ/' + str(image['pr_type']) + '/' + str(image_id) + ".png"
        f = open(path, 'wb')
        f.write(image['image_file'])
        f.close()
        print("Fetched image (id={0}) into path {1} | Owner: {2}".format(image_id, path, image['username']))
        return image

    def _upload(self, image):
        pr_type = image['pr_type']
        if pr_type == -1:
            return
        elif pr_type == 0:
            path = '../RealSR/results/Sharpic-SR/DIV2K/' + str(image['id']) + ".png"
        elif pr_type == 1:
            path = '../BOPB/result/old/final_output/' + str(image['id']) + ".png"
        elif pr_type == 2:
            path = '../BOPB/result/old_w_scratch/final_output/' + str(image['id']) + ".png"
        elif pr_type == 3:
            path = '../waifu2x/results/' + str(image['id']) + ".png"
        else:
            raise ValueError("Error: up value is not 0, 1, 2 or 3")
        print("Uploading ", path)
        assert os.path.exists(path), "Error: path does not exist"
        file_size = os.path.getsize(path)
        f = open(path, 'rb')

        file_data = f.read()

        # sha256 object create
        sha256 = hashlib.sha256()
        # sha256 update
        sha256.update(file_data)
        image['image_hash'] = sha256.hexdigest()

        self.minioClient.fput_object("images", image['image_hash'], path)

        # insert
        self.curs.execute("INSERT INTO processed_image(id, username, image_name, image_hash, size, up) VALUES (%s, %s, %s, %s, %s, %s) RETURNING id",
                          (image['id'], image['username'], image['image_name'], image['image_hash'], file_size, pr_type))
        self.conn.commit()
        f.close()
        print("Stored image(id={0}) into DB".format(image['id']))

    def process_db(self, image_id_list):

        image_list = []
        for image_id in image_id_list:
            # pass
            image_list.append(self._download(image_id))

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

        for image in image_list:
            self._upload(image)

        print("Finished processing")

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
