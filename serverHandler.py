'''
Python script for server to make image SR.
Run shell file in here.
'''

import os

def superResolution():
    os.system('sh exec.sh')


def checkServer():

    exist = False # default set as False

    print(f'Check storage server if there are pictures to be handled.')
    print(f'Return True when exist, else False')

    '''
    Check server
    ...
    '''

    return exist


if __name__ == '__main__':

    # Check if there are photos/videos
    if (checkServer == True):
        superResolution()
    else:
        # keep waiting
        print(f'There are nothing to be handled')
