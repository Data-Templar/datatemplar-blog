## Created the 03/08/2019
## By Quentin BEDENEAU
## External libs: PIL
## Requirements : argpase, sys, os
##
## This script remove all metadata of image files present in the current folder.
## Possibility to do it recursively for each sub-folder
## Option to define the targeted folder.

try:
    from PIL import Image
except ImportError as e:
    print("PIL library absent. Install it first")
import argparse, sys, os

extension_list = [".png",".PNG", ".gif", ".GIF", ".jpg", ".JPG", ".jpeg" , ".JPEG", ".jif" , "JIF", ".jfif", ".JFIF" , ".tif" , ".TIF", ".tiff" , ".TIFF" ]

# Argument creation
parser = argparse.ArgumentParser()
parser.add_argument("--target", help="Optionnal target folder", default=os.getcwd())
parser.add_argument("-r","--recurse", help="Action on all sub-folder", action='store_true')
args = parser.parse_args()
root_dir = args.target
recursevely = args.recurse

def list_images(dir):
    image_list  = []
    for file in os.listdir(dir):
        ext = os.path.splitext(file)[1]
        if ext.lower() not in extension_list:
            continue
        image_list.append(os.path.join(dir,file))
    if len(image_list)==0:
        print("no image in directory %s" % dir)
    return image_list

def removeMetadata(image_list):
    for img in image_list:
        print("Removing metadata of %s" % (img))
        image_file = open(img,'rb')
        image = Image.open(image_file)

        # next 3 lines strip exif
        image_data = list(image.getdata())
        image_without_exif = Image.new(image.mode, image.size)
        image_without_exif.putdata(image_data)

        image_without_exif.save(img)

def recurse(dir):
    for entry in os.scandir(dir):
        if entry.is_file():
            removeMetadata(list_images(dir))
        else:
            recurse(entry.path)

if recursevely:
    print("Script starting recursively")
    recurse(root_dir)
else:
    print("Script started for current directory")
    removeMetadata(list_images(root_dir))

print("End of script")
