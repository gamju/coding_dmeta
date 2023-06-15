import subprocess
import argparse
import os
def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--image_file_name', type=str, default = 'example.jpg',
                        help='Path to the model script.')
    parser.add_argument('--M', type=str, default = 3,
                        help='divide image with columns.')
    
    parser.add_argument('--N', type=str, default = 2,
                        help='divide image with rows.')
    return parser.parse_args()

args = parse_args()
os.makedirs("dataset", exist_ok = True)
os.makedirs("result", exist_ok = True)
input_folder_name = "dataset/{}/".format(args.image_file_name[:-4])
os.makedirs(input_folder_name, exist_ok = True)
input_folder_name = "dataset/{}/{}x{}/".format(args.image_file_name[:-4], args.M, args.N)
os.makedirs(input_folder_name, exist_ok = True)
output_folder_name = "result/{}/".format(args.image_file_name[:-4])
os.makedirs(input_folder_name, exist_ok = True)
output_folder_name = "result/{}/{}x{}/".format(args.image_file_name[:-4], args.M, args.N)
os.makedirs(output_folder_name, exist_ok = True)
subprocess.call(['python', 'cut_image.py', "--image_file_name={}".format(args.image_file_name), "--M={}".format(args.M), "--N={}".format(args.N), "--output_folder_name={}".format(input_folder_name)])
subprocess.call(['python', 'merge_image.py', "--input_folder_path={}".format(input_folder_name), "--output_folder_path={}".format(output_folder_name)])
