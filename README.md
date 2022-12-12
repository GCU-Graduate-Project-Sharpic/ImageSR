# Sharpic - image super resolution

Sharpic-image super resolution(= sr) is a simple image super resolution tool.  
It uses the [waifu2x-ncnn-vulkan](https://github.com/nihui/waifu2x-ncnn-vulkan), [tencent-realSR](https://github.com/Tencent/Real-SR) and [microsoft-bring-old-photos-back-to-life](https://github.com/microsoft/Bringing-Old-Photos-Back-to-Life) models.  

## Result

### waifu2x-ncnn-vulkan
<img src="figures/ex_waifu.png" width="50%" height="50%" alt="waifu">

### tencent-realSR
<img src="figures/ex_sr.png" width="50%" height="50%" alt="realsr">

### microsoft-bring-old-photos-back-to-life
<img src="figures/ex_rst1.png" width="50%" height="50%" alt="old">
<img src="figures/ex_rst2.png" width="50%" height="50%" alt="old">


## Usage 

### 1. Install

```bash
$ git clone https://github.com/GCU-Sharpic/sharpic-imagesr
$ cd sharpic-imagesr
```

```bash
$ pip install -r requirements.txt
$ (requirements will be added later)
```

### 2. Run

```bash
$ python main.py 
```

### 3. Select the model
You can select the model you want to use in sharpic-web. 
