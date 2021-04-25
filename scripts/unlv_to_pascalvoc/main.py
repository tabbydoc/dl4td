import sys
import os
import getopt
from collections import defaultdict
from xml.etree.ElementTree import ElementTree
import xml.etree.ElementTree as ET
import shutil
import csv
import fnmatch
from PIL import Image
import cv2


def main(argv):
    input_folder = ''
    output_folder = 'out'
    try:
        opts, args = getopt.getopt(argv, "hi:o:", ["input_folder=", "output_folder="])
    except getopt.GetoptError:
        print('test.py -i <input folder> -o <output folder>')
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print('test.py -i <input folder> -o <output folder>')
            sys.exit()
        elif opt in ("-i", "--i"):
            input_folder = arg
        elif opt in ("-o", "--o"):
            output_folder = arg

    is_folder = os.path.isdir(input_folder)

    if not is_folder:
        raise Exception(input_folder, "- It is not a folder")

    annotations_path = os.path.join(output_folder, "annotations")
    xmls_path = os.path.join(annotations_path, "xmls")
    images_path = os.path.join(output_folder, "images")
    input_file = os.path.join(input_folder, "xmls/train.csv")

    if os.path.exists(annotations_path):
        shutil.rmtree(annotations_path)
    if os.path.exists(images_path):
        shutil.rmtree(images_path)
    if os.path.exists(xmls_path):
        shutil.rmtree(xmls_path)

    os.makedirs(images_path)
    os.makedirs(annotations_path)
    os.makedirs(xmls_path)

    trainval_file = open(os.path.join(annotations_path, "trainval.txt"), 'w')

    images = dict()
    tables = defaultdict(list)

    print("save_images from " + input_folder)
    for dir_name, sub_dir_list, file_list in os.walk(input_folder):
        for file_name in fnmatch.filter(file_list, "*.png"):
            path = os.path.join(dir_name, file_name)
            name = os.path.splitext(os.path.split(path)[1])[0]
            save_path = os.path.join(images_path, name + ".jpeg")
            img = cv2.imread(path)
            height, width, channels = img.shape
            # if width > 2000 or height > 2000:
            #    img = cv2.resize(img, (0, 0), fx=0.5, fy=0.5)
            # img = transform_image(img)
            cv2.imwrite(save_path, img)
            images[name] = {"width": width, "height": height}

    with open(input_file, newline='') as csv_file:
        annotation_reader = csv.reader(csv_file)
        for row in annotation_reader:
            name = row[0]
            tables[name].append(row)

    for table in tables.keys():
        pascal_voc = process_row(tables[table], images)
        if pascal_voc is None:
            continue
        name = table
        name = os.path.splitext(os.path.split(name)[1])[0] + '.xml'
        pascal_voc_name = os.path.join(xmls_path, name)
        print(pascal_voc_name)
        pascal_voc.write(open(pascal_voc_name, 'w'), encoding='unicode')
        trainval_file.write(name + "\n")


def process_row(rows, images):
    for row in rows:
        annotation = ET.Element("annotation")
        tree = ElementTree(annotation)
        filename = ET.SubElement(annotation, "filename")
        name = row[0]
        name = os.path.splitext(os.path.split(name)[1])[0]
        filename.text = name + ".jpeg"
        size = ET.SubElement(annotation, "size")
        width = ET.SubElement(size, "width")
        width.text = str(images[name].get("width"))
        height = ET.SubElement(size, "height")
        height.text = str(images[name].get("height"))
        depth = ET.SubElement(size, "depth")
        depth.text = str(3)
        segmented = ET.SubElement(annotation, "segmented")
        segmented.text = str(0)
        obj = ET.SubElement(annotation, "object")
        obj_name = ET.SubElement(obj, "name")
        obj_name.text = "table"
        bndbox = ET.SubElement(obj, "bndbox")
        xmin = ET.SubElement(bndbox, "xmin")
        xmin.text = str(row[1])
        ymin = ET.SubElement(bndbox, "ymin")
        ymin.text = str(row[2])
        xmax = ET.SubElement(bndbox, "xmax")
        xmax.text = str(row[3])
        ymax = ET.SubElement(bndbox, "ymax")
        ymax.text = str(row[4])
    return tree


def transform_image(img):
    bimage = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
    ret, bimage = cv2.threshold(bimage, 40, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)
    r = cv2.distanceTransform(bimage, distanceType=cv2.DIST_L2, maskSize=5)
    g = cv2.distanceTransform(bimage, distanceType=cv2.DIST_L1, maskSize=5)
    b = cv2.distanceTransform(bimage, distanceType=cv2.DIST_C, maskSize=5)
    img = cv2.merge((r, g, b))
    return img


if __name__ == "__main__":
    main(sys.argv[1:])
