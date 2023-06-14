import os, glob, cv2
import numpy as np


def mirroring(image):
    image = image[:, ::-1]
    return image

def flipping(image):
    image = image[::-1, :]
    return image

def inv_rotating(image):
    out_image = np.zeros([image.shape[1], image.shape[0], image.shape[2]])
    for y in range(out_image.shape[0]):
        for x in range(out_image.shape[1]):
            out_image[y,x] = image[image.shape[0] - x - 1, y]
    return out_image

def rotating(image):
    out_image = np.zeros([image.shape[1], image.shape[0], image.shape[2]])
    for y in range(out_image.shape[0]):
        for x in range(out_image.shape[1]):
            out_image[y,x] = image[x, image.shape[1] - y - 1]
    return out_image

def get_edge(image, h_start = 0, w_start = 0):
    h,w = image.shape[:2]
    top = image[0,:].astype(np.int)
    top_inv = image[0, ::-1].astype(np.int)
    bottom = image[-1,:].astype(np.int)
    bottom_inv = image[-1,::-1].astype(np.int)
    left = image[:,0].astype(np.int)
    left_inv = image[::-1,0].astype(np.int)
    right = image[:,-1].astype(np.int)
    right_inv = image[::-1,-1].astype(np.int)

    return {"left" : [[h_start, w_start], left], "left_inv" : [[h_start, w_start], left_inv], "top" : [[h_start, w_start], top], "top_inv" : [[h_start, w_start], top_inv], 
            "right" : [[h_start, w_start + w - 1], right], "right_inv" : [[h_start, w_start + w - 1], right_inv], 
            "bottom" : [[h_start + h - 1 , w_start], bottom], "bottom_inv" : [[h_start + h - 1, w_start], bottom_inv]}

def merging(base_image, target_image, base_dict, adding_key):
    moved_edge_dict = get_edge(target_image)
    for idx in adding_key:
        if idx in moved_edge_dict.keys()
    
    return base_image
                


def matching_line(base, target, target_num):
    base_image, base_edge_dict = base
    target_image, target_edge_dict = target
    score = 100000000
    score_interact = ""

    base_edge_key_list = list(base_edge_dict.keys())
    target_edge_key_list = list(target_edge_dict.keys())

    matching_edge = {'base_key' : [], 'target_key' : []}
    for base_edge_key in base_edge_key_list:
        base_edge_list = base_edge_dict[base_edge_key]
        
        for target_edge_key in target_edge_key_list:
            target_edge_list = target_edge_dict[target_edge_key]
            _, target_edge_value = target_edge_list[0]

            for idx, base_edge_idx in enumerate(base_edge_list):
                _, base_edge_value = base_edge_idx
                # each target list is one
                # for target_edge in target_edge_list:
                if base_edge_value.shape != target_edge_value.shape:
                    continue
                else:
                    tmp_score = abs(target_edge_value - base_edge_value)
                    mean, std = tmp_score.mean(), tmp_score.std()
                    print(mean,std, target_num, base_edge_key, target_edge_key)
                    if mean < 10:
                        matching_edge['base_key'].append([base_edge_key, idx])
                        matching_edge['target_key'].append([target_edge_key])

    adding_base_key = []
    if matching_edge['base_key'].__len__() != 0:
        target_key = matching_edge['target_key'][0]
        base_key, _ = matching_edge['base_key'][0]
        #target_key len 2 mean direction and inverse
        # if target_key.find("inv") > 1:
        #     if target_key.find("left") > -1 or target_key.find("right"):
        #         target_image = inv_flipping(target_image)
        #     elif target_key.find("top") > -1 or target_key.find("bottom"):
        #         target_image = inv_mirroring(target_image)
        #0 left, 1 top, 2 right, 3 bottom
        base_arg_value = base_edge_key_list.index(base_key)
        target_arg_value = (target_edge_key_list.index(target_key))/2
        inverse_flag = False
        if target_key.find("inv") > -1:
            inverse_flag = True
        target_image = target_transform(target_image, base_arg_value, target_arg_value, inverse_flag)
        for matching_edge_idx in matching_edge['base_key']:
            base_edge_key, idx = matching_edge_idx
            strat_pos = base_edge_dict[base_edge_key][idx][0]
            base_edge_dict[base_edge_key].remove(base_edge_dict[base_edge_key][idx])
            adding_base_key.append([base_edge_key, strat_pos])
        
        
        #arg minus 0 mean flipping or mirroing, 1 mean rotating 
        base_image, base_edge_dict = merging(base_image, target_image, base_edge_dict, adding_base_key)

    return [base_image, base_edge_dict]

def base_init(base):
    base_image, base_dict = base
    for base_key in base_dict.keys():
        if base_key.find("inv") > -1:
            del base_dict[base_key]
    return [base_image,  base_dict]

def target_transform(image, base_direction, target_direction, inverse = False):

    if base_direction % 2 == 0:
        if inverse == True:
            image = flipping(image)
        if (base_direction + target_direction)%4 == 0:
            image = mirroring(image)
        elif (base_direction + target_direction)%4 == 1:
            image = rotating(image)
        elif (base_direction + target_direction)%4 == 3:
            image = mirroring(image)
            image = rotating(image)
    else:
        if inverse == True:
            image = mirroring(image)
        if (base_direction + target_direction)%4 == 1:
            image = inv_rotating(image)
        elif (base_direction + target_direction)%4 == 2:
            image = flipping(image)
        elif (base_direction + target_direction)%4 == 3:
            image = inv_rotating(image)
            image = flipping(image)
    return image
        
    
    
    
    


image_path_list = sorted(glob.glob("./dmeta/dataset/cut_image*.jpg"))
base_shape = cv2.imread(image_path_list[0]).shape[:2]
image_list = []
#image load and edgeline extract
for idx, image_path in enumerate(image_path_list):
    img = cv2.imread(image_path)
    h,w = img.shape[:2]
    if h != base_shape[0]:
        img = inv_rotating(img)
    image_list.append([img, get_edge(img)])
    cv2.imwrite("tmp_cut_image_{}.png".format(idx),img )

base_image = base_init(image_list[0])

for idx, image_idx in enumerate(image_list[1:]):
    print(base_image[0].shape, image_idx[0].shape)
    tmp_result = matching_line(base_image, image_idx, idx)



