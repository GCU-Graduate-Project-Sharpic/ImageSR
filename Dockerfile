FROM pytorch/pytorch
RUN apt-get -y update && \
    pip install numpy matplotlib librosa opencv-contrib-python
RUN apt-get -y install libgl1-mesa-glx
RUN apt-get -y install libglib2.0-0
COPY . .
CMD ["/bin/bash"]
