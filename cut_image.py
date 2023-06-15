import cv2
import random
import numpy as np
from itertools import product


#divide shape is True
def image_conditioning(image, height, width, columns, rows):

    #height conditioning
    divide_height = height/float(rows)
    cut_height = int(divide_height)
    if divide_height != cut_height:
        maximum_height = cut_height*rows
        image = image[:maximum_height, :]
    
    #width conditioning
    divide_width = width/float(columns)
    cut_width = int(divide_width)
    if divide_width != cut_width:
        maximum_width = cut_width*columns
        image = image[:, :maximum_width]  
    return image, cut_height, cut_width
    
 
def random_affine(image):
    org_image = image.copy()
    #mirroring mean vertical transformation
    if np.random.random(1) > 0.5:
        image = image[:, ::-1]
    #flipping mean horizontal transformation
    if np.random.random(1) > 0.5:
        image = image[::-1, :]
    #rotation mean 
    if np.random.random(1) > 0.5:
        # image = cv2.rotate(image, cv2.ROTATE_90_CLOCKWISE)
        #using python is late
        
        rotated_image = np.zeros([image.shape[1], image.shape[0], image.shape[2]])
        for y in range(rotated_image.shape[0]):
            for x in range(rotated_image.shape[1]):
                rotated_image[y,x] = image[x, image.shape[1] - y - 1]
        image = rotated_image

    return image

def cut_image(image_path, columns, rows):
    cut_images = []
    image = cv2.imread(image_path)
    h,w = image.shape[:2]
    image, cut_height, cut_width = image_conditioning(image, h, w, columns, rows)
    cv2.imwrite("conditioned_image.jpg", image)
    split_image_idx = np.arange(columns * rows)
    np.random.shuffle(split_image_idx)
    for idx, [row, col] in enumerate(product(range(1, rows + 1), range(1, columns + 1))):
        split_image = image[(row-1)*cut_height:row*cut_height, (col-1)*cut_width:col*cut_width]
        affined_image = random_affine(split_image)
        cut_images.append(affined_image)
        cv2.imwrite("cut_image_{}.jpg".format(split_image_idx[idx]), affined_image)
    
    return cut_images

cut_image("dmeta/example.jpg", 3,3)