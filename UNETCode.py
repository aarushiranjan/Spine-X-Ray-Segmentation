import os
import sys
import random

import numpy as np
import cv2
import matplotlib.pyplot as plt

import tensorflow as tf
from tensorflow import keras
class DataGen(keras.utils.Sequence):
    def __init__(self, ids,target_image,dir, path, batch_size=8, image_size=128):
        self.ids = ids
        self.path = path
        self.batch_size = batch_size
        self.target_image = target_image
        self.image_size = image_size
        self.dir = dir
        self.on_epoch_end()
        
    def __load__(self, id_name):
        ## Path
        image_path = os.path.join(self.path, id_name,self.dir) + ".jpg"
        #print(image_path)
        mask_path = os.path.join(self.path, id_name, self.dir)
        #print(mask_path)
        all_masks = os.listdir(mask_path)
        #print(all_masks)
        ## Reading Image
        image = cv2.imread(image_path, 1)
        image = cv2.resize(image, (self.image_size, self.image_size))
        
        mask = np.zeros((self.image_size, self.image_size, 1))
        
        ## Reading Masks
        for name in all_masks:
            if name == self.target_image:
                _mask_path = os.path.join(mask_path,name) #mask_path + name
                #print(_mask_path)
                _mask_image = cv2.imread(_mask_path, -1)
                _mask_image = cv2.resize(_mask_image, (self.image_size, self.image_size)) #128x128
                _mask_image = np.expand_dims(_mask_image, axis=-1)
                mask = np.maximum(mask, _mask_image)
            
        ## Normalizaing 
        image = image/255.0
        mask = mask/255.0
        
        return image, mask
    
    def __getitem__(self, index):
        #print("length of ids" ,len(self.ids))
        if(index+1)*self.batch_size > len(self.ids):
            self.batch_size = len(self.ids) - index*self.batch_size
        
        files_batch = self.ids[index*self.batch_size : (index+1)*self.batch_size]
        
        image = []
        mask  = []
        
        for id_name in files_batch:
            _img, _mask = self.__load__(id_name)
            image.append(_img)
            mask.append(_mask)
            
        image = np.array(image)
        mask  = np.array(mask)
        
        return image, mask
    
    def on_epoch_end(self):
        pass
    
    def __len__(self):
        return int(np.ceil(len(self.ids)/float(self.batch_size)))
image_size = 128
#image_size_y = 151
train_path = "DAMAGED"
epochs = 2
batch_size = 8

## Training Ids
train_ids = next(os.walk(train_path))[1]
#print(train_ids)
## Validation Data Size
val_data_size = 10

valid_ids = train_ids[:val_data_size]
train_ids = train_ids[val_data_size:]
#print(valid_ids)
target_image = "Ap_Vertebra.png"
gen = DataGen(train_ids,target_image,"AP" ,train_path, batch_size=batch_size, image_size=image_size)
x, y = gen.__getitem__(0)
#print(x.shape, y.shape)

# r = random.randint(0, len(x)-1)

# fig = plt.figure()
# fig.subplots_adjust(hspace=0.4, wspace=0.4)
# ax = fig.add_subplot(1, 2, 1)
# ax.imshow(x[r])
# ax = fig.add_subplot(1, 2, 2)
# ax.imshow(np.reshape(y[r], (image_size, image_size)), cmap="gray")
# plt.show()

def down_block(x, filters, kernel_size=(3, 3), padding="same", strides=1):
    c = keras.layers.Conv2D(filters, kernel_size, padding=padding, strides=strides, activation="relu")(x)
    c = keras.layers.Conv2D(filters, kernel_size, padding=padding, strides=strides, activation="relu")(c)
    p = keras.layers.MaxPool2D((2, 2), (2, 2))(c)
    return c, p

def up_block(x, skip, filters, kernel_size=(3, 3), padding="same", strides=1):
    us = keras.layers.UpSampling2D((2, 2))(x)
    concat = keras.layers.Concatenate()([us, skip])
    c = keras.layers.Conv2D(filters, kernel_size, padding=padding, strides=strides, activation="relu")(concat)
    c = keras.layers.Conv2D(filters, kernel_size, padding=padding, strides=strides, activation="relu")(c)
    return c

def bottleneck(x, filters, kernel_size=(3, 3), padding="same", strides=1):
    c = keras.layers.Conv2D(filters, kernel_size, padding=padding, strides=strides, activation="relu")(x)
    c = keras.layers.Conv2D(filters, kernel_size, padding=padding, strides=strides, activation="relu")(c)
    return c

def UNet():
    f = [16, 32, 64, 128, 256]
    inputs = keras.layers.Input((image_size, image_size, 3))
    
    p0 = inputs
    c1, p1 = down_block(p0, f[0]) #128 -> 64
    c2, p2 = down_block(p1, f[1]) #64 -> 32
    c3, p3 = down_block(p2, f[2]) #32 -> 16
    c4, p4 = down_block(p3, f[3]) #16->8
    
    bn = bottleneck(p4, f[4])
    
    u1 = up_block(bn, c4, f[3]) #8 -> 16
    u2 = up_block(u1, c3, f[2]) #16 -> 32
    u3 = up_block(u2, c2, f[1]) #32 -> 64
    u4 = up_block(u3, c1, f[0]) #64 -> 128
    
    outputs = keras.layers.Conv2D(1, (1, 1), padding="same", activation="sigmoid")(u4)
    model = keras.models.Model(inputs, outputs)
    return model

model = UNet()
model.compile(optimizer="adam", loss="binary_crossentropy", metrics=["acc"])
model.summary()


train_steps = len(train_ids)//batch_size
valid_steps = len(valid_ids)//batch_size
#print("training steps")
#print(train_steps,valid_steps)

target_images_ap= {"Ap_Vertebra.png","Ap_Pedicle.png","Ap_Spinous_Process.png"}
target_images_lat = {"Lat_Anterior_Vertebral_Line.png","Lat_Disk_Height.png","Lat_Posterior_Vertebral_Line.png","Lat_Spinous_Process.png","Lat_Vertebra.png"}

target_dir = {"AP","LAT"}

train_path = "DAMAGED"
for dir in target_dir:
	if dir == "AP":
		target_list = target_images_ap
	else:
		target_list = target_images_lat
		
	for target in target_list:
		#print("Choosing target: ",target)
		train_gen = DataGen(train_ids, target, dir,train_path, image_size=image_size, batch_size=batch_size)
		valid_gen = DataGen(valid_ids, target, dir, train_path, image_size=image_size, batch_size=batch_size)
		model.fit_generator(train_gen, validation_data=valid_gen, steps_per_epoch=train_steps, validation_steps=valid_steps,epochs=epochs)
		model.save_weights("UNetW_"+dir+"_"+target.split('.')[0]+".h5")
## Save the Weights
#model.save_weights("UNetW.h5")

print("Fininshed and saves weights!")

valid_gen = DataGen(valid_ids, "Lat_Disk_Height.png", "LAT", train_path, image_size=image_size, batch_size=batch_size)
# ## Dataset for prediction
x, y = valid_gen.__getitem__(1)
print(x.shape, y.shape)
result = model.predict(x)
##result = result > 0.1
# #print(result2)
# #print(result[0],result[1])
fig = plt.figure()
fig.subplots_adjust(hspace=0.4, wspace=0.4)

ax = fig.add_subplot(1, 2, 1)
ax.imshow(np.reshape(y[0]*255, (image_size, image_size)), cmap="gray")

ax = fig.add_subplot(1, 2, 2)
ax.imshow(np.reshape(result[0]*255, (image_size, image_size)), cmap="gray")
plt.show()

fig = plt.figure()
fig.subplots_adjust(hspace=0.2, wspace=0.2)

ax = fig.add_subplot(1, 2, 1)
ax.imshow(np.reshape(y[1]*255, (image_size, image_size)), cmap="gray")

ax = fig.add_subplot(1, 2, 2)
ax.imshow(np.reshape(result[1]*255, (image_size, image_size)), cmap="gray")
plt.show()
