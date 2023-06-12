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

def get_edge(image):
    top = image[0,:].astype(np.int)
    top_inv = image[0, ::-1].astype(np.int)
    bottom = image[-1,:].astype(np.int)
    bottom_inv = image[-1,::-1].astype(np.int)
    left = image[:,0].astype(np.int)
    left_inv = image[::-1,0].astype(np.int)
    right = image[:,-1].astype(np.int)
    right_inv = image[::-1,-1].astype(np.int)

    return {"top" : [top], "top_inv" : [top_inv], "bottom" : [bottom], "bottom_inv" : [bottom_inv], "left" : [left], "left_inv" : [left_inv], "right" : [right], "right_inv" : [right_inv]}

def matching_line(base, target, target_num):
    base_image, base_edge_dict = base
    target_image, target_edge_dict = target
    score = 100000000
    score_interact = ""

    base_edge_key_list = list(base_edge_dict.keys())
    target_edge_key_list = list(base_edge_dict.keys())
    for base_edge_key in base_edge_key_list:
        base_edge_list = base_edge_dict[base_edge_key] 
        for target_edge_key in target_edge_key_list:
            target_edge_list = target_edge_dict[target_edge_key]

            for base_edge in base_edge_list:
                # each target list is one
                # for target_edge in target_edge_list:
                if base_edge.shape != target_edge_list[0].shape:
                    continue
                else:
                    tmp_score = abs(base_edge - target_edge_list[0])
                    mean, std = tmp_score.mean(), tmp_score.std()
                    print(mean,std, target_num, base_edge_key, target_edge_key )
                    if mean < score and mean < 10:
                        score = mean
                        score_interact = "{}.{}".format(base_edge_key, target_edge_key)

    # if score_interact != None:
    #     base_key, target_key = score_interact.split(".")
    #     target_key = target_key.split("_")
    #     if target_key.__len__():
            


    return [base_image, base_edge_dict]

def base_init(base):
    base_image, base_dict = base
    for base_key in base_dict.keys():
        if base_key.find("inv") > -1:
            base_dict[base_key] = []
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



