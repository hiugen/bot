import os
import json
import random
import imageio.v2 as imageio

rootDir = os.getcwd()
imageDirList = ["image1","image2","image3"]

def init():
    global imageDirList
    for imageDir in imageDirList: #处理每个图片文件夹
        os.chdir(os.path.join(rootDir,imageDir))
        image_list = os.listdir(os.path.join(rootDir,imageDir))
        config_path = os.path.join(os.path.join(rootDir,imageDir) , "config.json")
        # 若没初始化 TODO： 改为根据json判断是否初始化
        if "config.json" in image_list:
            image_list.remove("config.json")
        for j in range(len(image_list)):
            image = image_list[j]
            if image[-4:] == ".jpg" or image[-4:] == ".png":
                #with imageio.get_writer(image[0:-4]+'.gif', mode='I', fps=1) as writer:
                    #writer.append_data(imageio.imread(image))
                os.rename(image,image[0:-4]+'.gif')
                #os.remove(image)
            #for i in range(-1, -len(image), -1):
                #if image[i] == '.':
                    # print(str(j) + image[i:], image)
                    # TODO: 重命名改为001格式
                    #try:
                        #os.rename(image, str(j) + image[i:])
                    #finally:
                        #break
            # 改写json
        f = open(config_path, "w")
        f.write('{"inited" : true}')
        os.chdir(rootDir)
    print("load_image.py inited")

def random_image(image_dir):
    global imageDirList
    if image_dir not in imageDirList:
        print("image_dir: " + image_dir + " not in imageDirList")
        return -1
    os.chdir(os.path.join(rootDir,image_dir))
    image_list = os.listdir(os.path.join(rootDir,image_dir))
    image_list.remove("config.json")
    return os.path.join(os.path.join(rootDir,image_dir),image_list[random.randint(0,len(image_list)-1)])


init()
if __name__ == "__main__":
    print(random_image("image2"))




