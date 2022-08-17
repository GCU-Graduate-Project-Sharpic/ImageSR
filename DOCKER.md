## Docker settings (No longer support. Please follow README.md Pre-requirements. )

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
