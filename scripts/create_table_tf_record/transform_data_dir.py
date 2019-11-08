# input_folder = '\\home\\vasily\\PycharmProjects\\TestTensor\\data\\PascalVoc\\VOC2019'
# output_folder = '\\home\\vasily\\PycharmProjects\\TestTensor\\data\\PascalVoc\\VOC2019\\OUT'
# python \\home\\vasily\\PycharmProjects\\TestTensor\\create_table_tf_record\\transform_data_dir.py '\\home\\vasily\\PycharmProjects\\TestTensor\\data\\PascalVoc\\VOC2019' '\\home\\vasily\\PycharmProjects\\TestTensor\\data\\PascalVoc\\VOC2019\\OUT'


""""Program parameters:

1 - The path to the folder where the "Annotations" and "Images" directories are located.
2 - Path to the folder where to copy files.
3 - Folder name with xml files.
4 - The name of the folder with pictures.
5 - (optional) The value of the display parameter of the 'display_mode' output, which is described below.

Output display option.
    0 - Display only the completion message.
    1 - Display information about which files are being copied.
    2 - Display detailed information for each file.


Startup example:
    transform_data_dir.py 'D:\Input Dir' 'D:\Output Dir' Annotation Images 1

"""

import sys
import os
import shutil

input_folder = 'D:\\WORK'
output_folder = 'D:\\WORK\\OUT'
folder_ann = 'Annotations'
folder_img = 'Images'

count_files = 0

if len(sys.argv) == 5:
    input_folder = sys.argv[1]
    output_folder = sys.argv[2]
    folder_ann = sys.argv[3]
    folder_img = sys.argv[4]
    display_mode = 1
else:
    if len(sys.argv) == 6:
        input_folder = sys.argv[1]
        output_folder = sys.argv[2]
        folder_ann = sys.argv[3]
        folder_img = sys.argv[4]
        display_mode = int(sys.argv[5])
    else:
        if len(sys.argv) < 5:
            print("ERROR! Not enough parameters")
            sys.exit(1)
        else:
            print("ERROR! Too many parameters")
            sys.exit(1)

if display_mode == 2:
    print("\nParams:\n-" + sys.argv[1] + "\n-" + sys.argv[2] + "\n-" + sys.argv[3] + "\nLength=" + str(
        len(sys.argv)) + "\n")

try:
    os.mkdir(output_folder + '\\annotations')
    os.mkdir(output_folder + '\\annotations\\xmls')
    os.mkdir(output_folder + '\\images')
except OSError:
    print("Create directory %s failed. Maybe it already exists." % output_folder)
else:
    if display_mode != 0:
        print("Directory successfully created %s" % output_folder)

files = os.listdir(input_folder + '\\' + folder_ann)

xml_folder = os.path.join(output_folder, "annotations\\xmls")
trainval_path = os.path.join(output_folder, "annotations")
img_folder = os.path.join(output_folder, "images")

f = open(trainval_path + '\\' + 'trainval.txt', 'w')

for xml_file in files:
    if xml_file.endswith('.xml'):
        count_files += 1
        ann_path_in = os.path.join(input_folder, folder_ann + '\\' + xml_file)
        if display_mode == 2:
            print("Xml file - " + ann_path_in)
        ann_path_out = os.path.join(xml_folder, xml_file)
        if display_mode == 2:
            print("Xml file copied - " + ann_path_out)
        file_name = xml_file[:-4]
        if display_mode == 2:
            print("File name - " + str(file_name))
        f.write(str(file_name) + '\n')

        img_path_in = os.path.join(input_folder, folder_img + '\\' + file_name + '.jpeg')
        if display_mode == 2:
            print("Jpeg file - " + img_path_in)
        img_path_out = os.path.join(img_folder, file_name + '.jpeg')
        if display_mode == 2:
            print("Jpeg file copied - " + img_path_out)
        shutil.copyfile(ann_path_in, ann_path_out)
        shutil.copyfile(img_path_in, img_path_out)
        if display_mode == 2 or display_mode == 1:
            print("%s file (xml and jpeg) copied!" % file_name)

        if display_mode == 2:
            print("==================")

print("Copying completed! \n Number of files:" + str(count_files))
f.close()

# with open(trainval_path + '\\' + 'text.txt') as f:
#     text = f.readlines()
#
# with open(trainval_path + '\\' + 'text.txt', 'w') as f:
#     f.writelines(text[:count_files-1])
