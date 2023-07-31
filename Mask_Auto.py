# -*- coding: utf-8 -*-
"""
Created on Tue Jul 16 22:47:02 2019

@author: Devil Hunter
"""

import glob
import json
import os
from natsort import natsorted
import os.path as osp
import numpy as np
import PIL.Image
import PIL.ImageDraw

folders = os.listdir("./NORMAL")
#print(folders)

def load_from_folder(folder):
    images = []
    sub_path = "./NORMAL/" + folder
    for filename in os.listdir(sub_path):
        if any([filename.endswith(x) for x in ['.jpg', '.jpeg']]):
            tple = (folder, filename)
            images.append(tple)
    return images

all_images = []
for folder in folders:
	images = load_from_folder(folder)
	if images:
		#print(images)
		#print(os.path.splitext(images[0][1])[0]+','+os.path.splitext(images[1][1])[0])
		os.chdir('./NORMAL/'+folder)
		os.system('mkdir AP')
		os.system('mkdir LAT')
		# for single_img in images:
			# all_images.append(single_img)
		
		#for img in images:
		file_img_path_AP = images[0][1]
		file_img_path_LAT = images[1][1]
		file_json_path_AP = os.path.splitext(images[0][1])[0]+'.json'
		file_json_path_LAT = os.path.splitext(images[1][1])[0]+'.json'
		#####################			
		# for saving AP Mask
		#####################	
		img = PIL.Image.open(file_img_path_AP, 'r')
		json_annotation_path = natsorted(glob.glob(file_json_path_AP))
						
		for annotation in json_annotation_path:
			with open(annotation, encoding='utf-8') as f:  
				data = json.load(f)
							
			mask = np.zeros(img.size, dtype=np.uint8).transpose()
			mask = PIL.Image.fromarray(mask, '1')
			for shape in data["shapes"]:
				if "Vertebra" in shape["label"]:
					xy = [tuple(point) for point in shape["points"]]
					PIL.ImageDraw.Draw(mask).polygon(xy=xy, outline=1, fill=1)
					#mask.save("./xyz/" + file_img[0] + "/" + "Ap_Vertebra.png")
					mask.save("./AP/" +  "Ap_Vertebra.png")
								
			mask = np.zeros(img.size, dtype=np.uint8).transpose()
			mask = PIL.Image.fromarray(mask, '1')
			for shape in data["shapes"]:
				if "Pedicle" in shape["label"]:
					xy = [tuple(point) for point in shape["points"]]
					PIL.ImageDraw.Draw(mask).polygon(xy=xy, outline=1, fill=1)
					#mask.save("./xyz/" + file_img[0] + "/" + "Ap_Pedicle.png")
					mask.save("./AP/" +  "Ap_Pedicle.png")

			mask = np.zeros(img.size, dtype=np.uint8).transpose()
			mask = PIL.Image.fromarray(mask, '1')
			for shape in data["shapes"]:
				if "Spinous Process" in shape["label"]:
					xy = [tuple(point) for point in shape["points"]]
					PIL.ImageDraw.Draw(mask).polygon(xy=xy, outline=1, fill=1)
					#mask.save("./xyz/" + file_img[0] + "/" + "Ap_Spinous_Process.png")
					mask.save("./AP/" +  "Ap_Spinous_Process.png")
					
		#####################			
		# for saving LAT Mask
		#####################
		img = PIL.Image.open(file_img_path_LAT, 'r')
		json_annotation_path = natsorted(glob.glob(file_json_path_LAT))			
		for annotation in json_annotation_path:
			with open(annotation, encoding='utf-8') as f:
				data = json.load(f)

			mask = np.zeros(img.size, dtype=np.uint8).transpose()
			mask = PIL.Image.fromarray(mask, '1')
			for shape in data["shapes"]:
				if "Vertebra" in shape["label"]:
					xy = [tuple(point) for point in shape["points"]]
					PIL.ImageDraw.Draw(mask).polygon(xy=xy, outline=0, fill=1)
					
					mask.save("./LAT/" +  "Lat_Vertebra.png")
					
			mask = np.zeros(img.size, dtype=np.uint8).transpose()
			mask = PIL.Image.fromarray(mask, '1')
			for shape in data["shapes"]:           
				if "Disk Height" in shape["label"]:
					xy = [tuple(point) for point in shape["points"]]
					PIL.ImageDraw.Draw(mask).polygon(xy=xy, outline=1, fill=1)
					
					mask.save("./LAT/" +  "Lat_Disk_Height.png")
					
			mask = np.zeros(img.size, dtype=np.uint8).transpose()
			mask = PIL.Image.fromarray(mask, '1')
			for shape in data["shapes"]:           
				if "Anterior Vertebral Line" in shape["label"]:
					xy = [tuple(point) for point in shape["points"]]
					PIL.ImageDraw.Draw(mask).polygon(xy=xy, outline=1, fill=1)
					
					mask.save("./LAT/" +  "Lat_Anterior_Vertebral_Line.png")
					
			mask = np.zeros(img.size, dtype=np.uint8).transpose()
			mask = PIL.Image.fromarray(mask, '1')
			for shape in data["shapes"]:           
				if "Posterior Vertebral Line" in shape["label"]:
					xy = [tuple(point) for point in shape["points"]]
					PIL.ImageDraw.Draw(mask).polygon(xy=xy, outline=1, fill=1)
					
					mask.save("./LAT/" +  "Lat_Posterior_Vertebral_Line.png")

			mask = np.zeros(img.size, dtype=np.uint8).transpose()
			mask = PIL.Image.fromarray(mask, '1')
			for shape in data["shapes"]:    
				if "Spinous Process" in shape["label"]:
					xy = [tuple(point) for point in shape["points"]]
					PIL.ImageDraw.Draw(mask).polygon(xy=xy, outline=1, fill=1)

					mask.save("./LAT/" +  "Lat_Spinous_Process.png")
		os.chdir('../../')