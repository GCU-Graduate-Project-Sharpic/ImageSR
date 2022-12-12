"""
Python for generate script for waifu2x-ncnn-vulkan
input image path: ../connects/LQ/3/
output image path: ./images/output/

noise level = default 2, get from parameter
scale = default 2, get from parameter
"""

import os
import argparse


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--noise_level', type=str, default='2')
    parser.add_argument('--scale', type=str, default='2')
    return parser.parse_args()


def main():

    args = parse_args()
    noise_level = args.noise_level
    scale = args.scale

    # get all image name
    image_name_list = os.listdir('../../connects/LQ/3/')

    # generate script
    with open('../waifu2x_runner.sh', 'w') as f:
        for image_name in image_name_list:
            f.write('../waifu2x-ncnn-vulkan -i ../../connects/LQ/3/{0} -o ../results/{0} -n {1} -s {2}'
                    .format(image_name, noise_level, scale))
            f.write('\n')

    # run script
    os.system('chmod +x ../waifu2x_runner.sh')
    os.system('../waifu2x_runner.sh')


if __name__ == '__main__':
    main()
