FROM pytorch/pytorch
WORKDIR /usr/src
RUN apt-get -y -qq update && \
    pip install numpy matplotlib librosa opencv-contrib-python
COPY . .
CMD ["test.py"]
ENTRYPOINT ["python3"]
