FROM rocm/pytorch:rocm5.4_ubuntu20.04_py3.8_pytorch_1.12.1

RUN wget -qO - http://packages.lunarg.com/lunarg-signing-key-pub.asc | sudo apt-key add -
RUN wget -qO /etc/apt/sources.list.d/lunarg-vulkan-focal.list http://packages.lunarg.com/vulkan/lunarg-vulkan-focal.list
RUN apt update
RUN apt install -y mesa-vulkan-drivers
RUN apt install -y vulkan-sdk

WORKDIR /imagesr

COPY ./BOPB ./BOPB

WORKDIR /imagesr/BOPB/Face_Enhancement/models/networks/
RUN git clone https://github.com/vacancy/Synchronized-BatchNorm-PyTorch
RUN cp -rf Synchronized-BatchNorm-PyTorch/sync_batchnorm .

WORKDIR /imagesr/BOPB/Global/detection_models
RUN git clone https://github.com/vacancy/Synchronized-BatchNorm-PyTorch
RUN cp -rf Synchronized-BatchNorm-PyTorch/sync_batchnorm .

WORKDIR /imagesr/BOPB/Face_Detection/
RUN wget http://dlib.net/files/shape_predictor_68_face_landmarks.dat.bz2
RUN bzip2 -d shape_predictor_68_face_landmarks.dat.bz2

WORKDIR /imagesr/BOPB/Face_Enhancement/
RUN wget https://github.com/microsoft/Bringing-Old-Photos-Back-to-Life/releases/download/v1.0/face_checkpoints.zip
RUN unzip face_checkpoints.zip
WORKDIR /imagesr/BOPB/Global/
RUN wget https://github.com/microsoft/Bringing-Old-Photos-Back-to-Life/releases/download/v1.0/global_checkpoints.zip
RUN unzip global_checkpoints.zip

WORKDIR /imagesr/BOPB/
RUN pip install -r requirements.txt

WORKDIR /imagesr
COPY ./RealSR ./RealSR
COPY ./waifu2x ./waifu2x
COPY ./connects ./connects

WORKDIR /imagesr/connects
RUN pip install -r requirements.txt

CMD [ "python", "-u", "/imagesr/connects/main.py"]