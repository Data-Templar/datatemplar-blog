#!/usr/local/bin/python3

from xmlrpc.client import Boolean
import cv2
import argparse
import pathlib
from tqdm import tqdm

def ArgParser():
    # Construct the argument parser and parse the arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("-p", "--path", type=pathlib.Path, required=False, default='.', help="path of the directory containing every photo, default current location")
    parser.add_argument("-ext", "--extension", required=False, default='.JPG', help="extension name. default is 'JPG'.")
    parser.add_argument("-o", "--output", type=pathlib.Path, required=False, help="output video file")
    parser.add_argument("-f", "--FPS", type=float, required=False, default=20.0, help="FPS rate of the video")
    parser.add_argument("-r", "--recursive", required=False, action='store_true', help="If set will perform a recursive loop on all subfolder creating a dedicated film for each folder")
    return vars(parser.parse_args())

def create_video(dir_path,output):
    # Add only files (aka images) with the correct extension
    images = []
    globtxt = '*'+ext
    for f in dir_path.glob(globtxt):
         images.append(f)

    if len(images) == 0:
        return

    # Determine the width and height from the first image
    frame = cv2.imread(str(images[0]))
    #cv2.imshow('video',frame) # Not necessary to visualise the picture before integrating it
    height, width, channels = frame.shape

    # Define the codec and create VideoWriter object
    fourcc = cv2.VideoWriter_fourcc(*'mp4v') # Be sure to use lower case
    out = cv2.VideoWriter(str(output), fourcc, FPS, (width, height))

    for image in tqdm(images):
        frame = cv2.imread(str(image))

        out.write(frame) # Write out frame to video

        # Display the advance by showing the integrated image
        #cv2.imshow('video',frame)
        #if (cv2.waitKey(1) & 0xFF) == ord('q'): # Hit `q` to exit
        #    break

    # Release everything if job is finished
    out.release()
    cv2.destroyAllWindows()
    print("The output video is {}".format(output))


if __name__ == '__main__':
    # Arguments
    parsedArgs = ArgParser()
    dir_path = parsedArgs['path']
    ext = parsedArgs['extension']
    output = parsedArgs['output']
    FPS = parsedArgs['FPS']
    recursive = parsedArgs['recursive']
   
    if recursive:
        print("recursive activate")
        folders=[x for x in dir_path.iterdir() if x.is_dir()]
        i=0
        for folder in folders:
            print("i vaut %d" % (i))
            filename="output"+str(i)+".mp4"
            if output is None or output =="":
                # Default output path
                outputname = pathlib.Path(dir_path.parent,filename)
            elif output.suffix == "":
                outputname = output.joinpath(filename)
            print(folder)
            print(outputname)
            create_video(folder,outputname)
            i=i+1

    else:
        print("not recursive")
        if output is None or output =="":
            # Default output path
            output = pathlib.Path(dir_path.parent,"output.mp4")
        elif output.suffix == "":
            output = output.joinpath('output.mp4')
        create_video(dir_path,output)

    
        

    

    


    