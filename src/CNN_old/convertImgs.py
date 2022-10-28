#This script converts all images in a folder to a format fit for NN training: 256x256 monochrome, with three sets (train, valid, test)

import random
from PIL import Image, ImageOps
import os
import math
import shutil

# ------ CONFIG ----- #

targetShape = (256,256) #Target res of the images
sizeThresh = 50 #Min square resolution for it to be accepted

trainPercentage = 80 /100
validPercentage = 15 /100
testPercentage = 5 /100

outputPath = "C:\\Users\\pierr\\Desktop\\Processed_data"
inputPath = "C:\\Users\\pierr\\Desktop\\Extra_data"

data_augmentation = True

# ---- AUGMENT FUNCTION ---- #

def augment(name, img):
    output = [(name,img)]

    output.append( (name+"_rot1.png", img.rotate(90)) )
    output.append( (name+"_rot2.png", img.rotate(180)) )
    output.append( (name+"_rot3.png", img.rotate(270)) )

    output.append( (name+"_fliprot1.png", ImageOps.mirror(img).rotate(90)) )
    output.append( (name+"_fliprot2.png", ImageOps.mirror(img).rotate(180)) )
    output.append( (name+"_fliprot3.png", ImageOps.mirror(img).rotate(270)) )

    return output




# ---- IMAGE HANDLING ---- #

objImgs = os.listdir(f"{inputPath}\\Obj")
noObjImgs = os.listdir(f"{inputPath}\\NoObj")

random.shuffle(objImgs)
random.shuffle(noObjImgs)

doneObj = []
doneNoObj = []

os.makedirs(f"{outputPath}\\Obj", exist_ok=True)
for x in objImgs:
    im = Image.open(f"{inputPath}\\Obj\\{x}")
    if im.size > (sizeThresh, sizeThresh):
        im = ImageOps.grayscale(im)
        im = ImageOps.fit(im, targetShape, method=Image.NEAREST)

        if data_augmentation:
            for (title, image) in augment(x, im):
                doneObj.append(title)
                image.save(f"{outputPath}\\Obj\\{title}")
        else:
            im.save(f"{outputPath}\\Obj\\{x}")
            doneObj.append(x)


    im.close()

os.makedirs(f"{outputPath}\\NoObj", exist_ok=True)
for x in noObjImgs:
    im = Image.open(f"{inputPath}\\NoObj\\{x}")
    if im.size > (sizeThresh, sizeThresh):
        im = ImageOps.grayscale(im)
        im = ImageOps.fit(im, targetShape, method=Image.NEAREST)

        if data_augmentation:
            for title, image in augment(x, im):
                image.save(f"{outputPath}\\NoObj\\{title}")
                doneNoObj.append(title)
        else:
            im.save(f"{outputPath}\\NoObj\\{x}")
            doneNoObj.append(x)

    im.close()

    if len(doneNoObj) > len(doneObj): #We want as many NoObj as Objs
        break

# ---- SET GENERATION ---- #

l = len(doneObj)
Obj = doneObj[:math.floor(l*trainPercentage)], doneObj[math.floor(l*trainPercentage):math.floor(l*(trainPercentage+validPercentage))], doneObj[math.floor(l*(trainPercentage+validPercentage)):]

l = len(doneNoObj)
NoObj = doneNoObj[:math.floor(l*trainPercentage)], doneNoObj[math.floor(l*trainPercentage):math.floor(l*(trainPercentage+validPercentage))], doneNoObj[math.floor(l*(trainPercentage+validPercentage)):]

for i,set in enumerate(["train", "valid", "test"]):
    os.makedirs(f"{outputPath}\\{set}\\Obj", exist_ok=True)
    for name in Obj[i]:
        shutil.move(f"{outputPath}\\Obj\\{name}", f"{outputPath}\\{set}\\Obj")

for i,set in enumerate(["train", "valid", "test"]):
    os.makedirs(f"{outputPath}\\{set}\\NoObj", exist_ok=True)
    for name in NoObj[i]:
        shutil.move(f"{outputPath}\\NoObj\\{name}", f"{outputPath}\\{set}\\NoObj")