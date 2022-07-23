FROM pytorch/pytorch:1.6.0-cuda10.1-cudnn7-devel 
WORKDIR /usr/src
RUN apt-get -y -qq update && \
    pip install numpy matplotlib librosa opencv-contrib-python
COPY . .
CMD ["test.py"]
ENTRYPOINT ["python3"]
