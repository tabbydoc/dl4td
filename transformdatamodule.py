import os
import shutil
from termcolor import colored
import xml.etree.ElementTree as ET
import copy
import sys

_copy_suffix = 1
_slash = os.sep


def Ssum(a, b):
    a += b
    return a


def transform(input_folder, output_folder, folder_ann, folder_img, display_mode):
    count_files = 0
    try:
        os.mkdir(output_folder + _slash + 'annotations')
        os.mkdir(output_folder + _slash + 'annotations' + _slash + 'xmls')
        os.mkdir(output_folder + _slash + 'images')
    except OSError:
        print("Create directory %s failed. Maybe it already exists." % output_folder)
    else:
        if display_mode != 0:
            print("Directory successfully created %s" % output_folder)

    files = os.listdir(input_folder + _slash + folder_ann)

    xml_folder = os.path.join(output_folder, 'annotations' + _slash + 'xmls')
    trainval_path = os.path.join(output_folder, 'annotations')
    img_folder = os.path.join(output_folder, 'images')

    f = open(trainval_path + _slash + 'trainval.txt', 'w')

    for xml_file in files:
        if xml_file.endswith('.xml'):
            count_files += 1
            ann_path_in = os.path.join(input_folder, folder_ann + _slash + xml_file)
            if display_mode == 2:
                print("Xml file - " + ann_path_in)
            ann_path_out = os.path.join(xml_folder, xml_file)
            if display_mode == 2:
                print("Xml file copied - " + ann_path_out)
            file_name = xml_file[:-4]
            if display_mode == 2:
                print("File name - " + str(file_name))
            f.write(str(file_name) + '\n')

            img_path_in = os.path.join(input_folder, folder_img + _slash + file_name + '.jpeg')
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



def move_files(in_path, _debug, xmls_path, images_path):

    # files = os.listdir(in_path + "+ _slash +annotations+ _slash +xmls")
    files = os.listdir(os.path.join(in_path, 'annotations' + _slash + 'xmls'))
    for xml_file in files:
        if xml_file.endswith('.xml'):
            ann_path_in = os.path.join(in_path + _slash + 'annotations' + _slash + 'xmls' + _slash, xml_file)
            if _debug == 1:
                print(colored("-File xml input - " + ann_path_in, 'green'))
            ann_path_out = os.path.join(xmls_path, xml_file)
            if _debug == 1:
                print(colored("-File xml output - " + ann_path_out, 'green'))
            file_name = xml_file[:-4]
            if os.path.exists(ann_path_out):
                if _debug == 1:
                    print(colored("-File exist! Run copy proc", 'green'))
                global _copy_suffix
                new_filename = file_name + '_' + str(_copy_suffix)
                ann_path_out = os.path.join(xmls_path, new_filename + '.xml')
                if _debug == 1:
                    print(colored("-New xml path - " + ann_path_out, 'green'))
                shutil.copyfile(ann_path_in, ann_path_out)

                xml_tree = ET.parse(ann_path_out)
                new_xml_tree = copy.deepcopy(xml_tree)
                filename_img = new_xml_tree.find('filename')
                filename_img.text = new_filename + '.jpeg'
                new_xml_tree.write(ann_path_out)

                img_path_in = os.path.join(in_path + _slash + 'images' + _slash, file_name + '.jpeg')
                img_path_out = os.path.join(images_path, new_filename + '.jpeg')
                shutil.copyfile(img_path_in, img_path_out)
                _copy_suffix += 1

            else:
                img_path_in = os.path.join(in_path + _slash + 'images' + _slash, file_name + '.jpeg')
                img_path_out = os.path.join(images_path, file_name + '.jpeg')
                shutil.copyfile(ann_path_in, ann_path_out)
                shutil.copyfile(img_path_in, img_path_out)


def delete_excess(in_path):
    files = os.listdir(in_path + _slash + 'annotations' + _slash + 'xmls')
    for xml_file in files:
            xml_tree = ET.parse(os.path.join(in_path + _slash + 'annotations' + _slash + 'xmls', xml_file))
            new_xml_tree = copy.deepcopy(xml_tree)
            filename_img = new_xml_tree.find('object')
            if filename_img is None:
                print('Delete file - ' + str(xml_file))
                os.remove(os.path.join(in_path  + _slash + 'annotations' + _slash + 'xmls', xml_file))
                file_name = xml_file[:-4]
                img = os.path.join(in_path  + _slash + 'images' + _slash, file_name + '.jpeg')
                os.remove(img)
