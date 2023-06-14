import os, glob, cv2
import numpy as np


def inv_mirroring(image):
    image = image[:, ::-1]
    return image

def inv_flipping(image):
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

def get_edge(image):
    h,w = image.shape[:2]
    top = image[0,:].astype(np.int)
    top_inv = image[0, ::-1].astype(np.int)
    bottom = image[-1,:].astype(np.int)
    bottom_inv = image[-1,::-1].astype(np.int)
    left = image[:,0].astype(np.int)
    left_inv = image[::-1,0].astype(np.int)
    right = image[:,-1].astype(np.int)
    right_inv = image[::-1,-1].astype(np.int)

    return {"left" : [[[0,0],left]], "left_inv" : [[[0,0],left_inv]], "top" : [[[0,0],top]], "top_inv" : [[[0,0],top_inv]], 
            "bottom" : [[[h-1,0],bottom]], "bottom_inv" : [[[h-1,0]],bottom_inv],  "right" : [[[0,w-1]],right], "right_inv" : [[[0,w-1]],right_inv]}

def horizontal_merging(base_image, target_image, edge_info, base_arg_value, target_arg_value, base_edge_dict):
    #arg%2 0 is flipping, 1 is mirroing
    if base_arg_value == target_arg_value:
        target_image = inv_mirroring(target_image)
        
    base_h,base_w = base_image.shape[:2]
    target_h,target_w = target_image.shape[:2]
    base_start_pos, base_edge = edge_info

    start_pos = [0,0]
    start_pos[0] = base_start_pos[0]
    if base_arg_value == 0:
        start_pos[1] = 0
    else:
        start_pos[1] = base_start_pos[1] + 1

    if start_pos[1] == 0:
        base_expand = np.zeros([base_h, base_w + target_w, base_image.shape[2]])
        base_expand[:, target_w : target_w + base_w] = base_image
        base_expand[start_pos[0]:start_pos[0] + target_h, :target_w] = target_image

        for base_keys in base_edge_dict.keys():
            for idx in range(base_edge_dict[base_keys].__len__()):
                base_start_idx = base_edge_dict[base_keys][idx][0]
                base_edge_dict[base_keys][idx][0] = [base_start_idx[0], base_start_idx[1] + target_w]
        base_edge_dict['left'].append([[start_pos[0], 0], target_image[:,0]])
        base_edge_dict['bottom'].append([[start_pos[0] + target_h, 0], target_image[-1,:]])
        base_edge_dict['top'].append([[start_pos[0], target_w], target_image[0,:]])
    
    elif start_pos[1] == base_w:
        base_expand = np.zeros([base_h, base_w + target_w, base_image.shape[2]])
        base_expand[:, : base_w] = base_image
        base_edge_dict['right'].append([[start_pos[0], start_pos[1]], target_image[:,-1]])
        base_edge_dict['bottom'].append([[start_pos[0] + target_h, start_pos[1]], target_image[-1,:]])
        base_edge_dict['top'].append([[start_pos[0], target_w], target_image[0,:]])
    else:
        base_image[start_pos[0] :start_pos[0] + target_h, start_pos[1] :start_pos[1] + target_w ] = target_image
            
    return base_image, base_edge_dict
                

def vertical_merging(image):
    return image

def matching_line(base, target, target_num):
    base_image, base_edge_dict = base
    target_image, target_edge_dict = target
    score = 100000000
    score_interact = ""

    base_edge_key_list = list(base_edge_dict.keys())
    target_edge_key_list = list(target_edge_dict.keys())

    matching_base_idx = 0
    matching_base_edge = 0

    for base_edge_key in base_edge_key_list:
        base_edge_list = base_edge_dict[base_edge_key] 
        for target_edge_key in target_edge_key_list:
            target_edge_list = target_edge_dict[target_edge_key]
            target_start_pos, target_edge = target_edge_list[0]

            for idx, base_edge_idx in enumerate(base_edge_list):
                _, base_edge = base_edge_idx
                # each target list is one
                # for target_edge in target_edge_list:
                if base_edge.shape != target_edge.shape:
                    continue
                else:
                    tmp_score = abs(base_edge - target_edge)
                    mean, std = tmp_score.mean(), tmp_score.std()
                    print(mean,std, target_num, base_edge_key, target_edge_key )
                    if mean < 10:
                        matching_base_idx = idx
                        matching_base_edge = base_edge_idx
                        score_interact = "{}.{}".format(base_edge_key, target_edge_key)

    
    if score_interact != None:
        base_key, target_key = score_interact.split(".")
        target_key = target_key.split("_")
        
        if target_key.find("inv") > -1:
            if target_key.find("left") > -1 or target_key.find("right"):
                target_image = inv_flipping(target_image)
            elif target_key.find("top") > -1 or target_key.find("bottom"):
                target_image = inv_mirroring(target_image)
        base_arg_value = base_edge_key_list.index(base_key)
        target_arg_value = (target_edge_key_list.index(target_key)+1)/2
        #arg minus 0 mean flipping or mirroing, 1 mean rotating 

        base_edge_dict[base_key].remove(base_edge_dict[base_key][matching_base_idx])                                 
        if (base_arg_value - target_arg_value)%2 == 0:  
            #max arg source, min arg target
            base_image, base_edge_dict = vertical_merging(base_image, target_image, matching_base_edge, base_arg_value, target_arg_value, base_edge_dict)
        else:
            base_image, base_edge_dict = horizontal_merging(base_image, target_image, matching_base_edge, base_arg_value, target_arg_value, base_edge_dict)

    return [base_image, base_edge_dict]

def base_init(base):
    base_image, base_dict = base
    for base_key in base_dict.keys():
        if base_key.find("inv") > -1:
            del base_dict[base_key]
    return [base_image,  base_dict]


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



