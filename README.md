# ImageSR
**IMPORTANT**  
Codes are cloned from [Tencent-RealSR](https://github.com/jixiaozhong/RealSR) project.  
In order to apply a model with very nice performance to the project, the cloned code was partially modified and fit to the project.  

**About ImageSR**  
ImageSR is a part of the "[Sharpic](https://github.com/GCU-Graduate-Project-Sharpic/Sharpic)", which automatically generate HQ image from LQ images. (Less than 2K).  
By using RealSR's kernel-estimation method, we were able to train by preparing a great dataset for the **real world**.  

  
We use super resolution algorithms below
- [EDSR (cv)](https://github.com/sanghyun-son/EDSR-PyTorch)
- [ESPCN (cv)](https://github.com/Lornatang/ESPCN-PyTorch)
- [Tencent RealSR](https://github.com/jixiaozhong/RealSR)
- [OpenCV & OpenCV contrib](https://github.com/opencv/opencv)

**We also want to train above algorithms(EDSR & ESPCN) using RealSR's dataset generator.**  

## Pre-requirements  
> You can simply match it by using docker  

## Training environment 
> NVIDIA Tesla P100 GPU (Colab Pro)  
> CUDA  
> pytorch  

> `Time consumption: (6H 30M)`

## Docker settings 

**IMPORTANT**  
> You can just simply clone the [Sharpic Repository](https://github.com/GCU-Graduate-Project-Sharpic/Sharpic) then build using makefile.  
> Or, if you want to simply run this SR method, You should follow below information.  

> 1. Build docker file  
> `docker build -t built_dockerfile .` (You can freely change the name of `built_dockerfile`)  
> 
> 2. Run to save docker images into repository  
> `docker run -itd --name torch_docker -v /home/hyun/share:/root/share -p 8888:8888 --restart=always built_dockerfile`  
> In above command, you can freely change `hyun` as your account ID and  
> `built_dockerfile` as name which you changed above.  
> 
> (Optinal) To use jupyter notebook as editor, follow below commands.  
> `conda install jupyter` <-- Install jupyter notebook in your docker  
> `jupyter notebook --ip=0.0.0.0 --port=8888 --allow-root` <-- Connect to your port

## Result (DIV2K 900-999) images 
- DIV2K 998 image (LR : HR), RealSR with Kernel Estimation  
<img src = "./figs/DIV2k_998.png">  

- DIV2K 998 image (LR : HR), EDSR without Kernel Estimation  
<img src = "./figs/edsr_cv.png">
