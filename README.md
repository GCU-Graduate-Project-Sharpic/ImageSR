# ImageSR
This is the part of the "Super resolution" project.  
It automatically generate HQ image from LQ images. (Less than 2K).  
  
We use super resolution algorithms below
- [EDSR](https://github.com/sanghyun-son/EDSR-PyTorch)
- [ESPCN](https://github.com/Lornatang/ESPCN-PyTorch)
- [OpenCV](https://github.com/opencv/opencv)

## Pre-requirements
> docker 

## Environment settings (추후 통합 뒤 변경 예정)
> 1. Build docker file  
> `docker build -t built_dockerfile .` (You can freely change the name of `built_dockerfile`)  
> 2. Run to save docker images into repository  
> `docker run -itd --name torch_docker -v /home/hyun/share:/root/share -p 8888:8888 --restart=always built_dockerfile`  
> In above command, you can freely change `hyun` as your account ID and  
> `built_dockerfile` as name which you changed above.  

## Execution (추후 수정 예정)
> `docker exec -it torch_docker bash`
