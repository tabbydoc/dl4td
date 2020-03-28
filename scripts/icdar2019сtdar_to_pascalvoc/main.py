import os
import fnmatch
from xml.etree.ElementTree import ElementTree
import xml.etree.ElementTree as ET
import shutil
import getopt
import sys
from PIL import Image

#input_path = "D:\Projects\PyCharm\TabbyPdf\DATA\ICDAR2019_cTDaR"
#output_path = "D:\Projects\PyCharm\TabbyPdf\DATA\ICDAR2019_CONVERT"

input_path = ""
output_path = ""

argv = sys.argv[1:]

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
        input_path = arg
    elif opt in ("-o", "--o"):
        output_path = arg

annotation_out = os.path.join(output_path, "annotations")
annotation_xml_out = os.path.join(annotation_out, "xmls")
image_out = os.path.join(output_path, "images")

if os.path.exists(annotation_out):
    shutil.rmtree(annotation_out)
if os.path.exists(annotation_xml_out):
    shutil.rmtree(annotation_xml_out)
if os.path.exists(image_out):
    shutil.rmtree(image_out)

os.makedirs(annotation_out)
os.makedirs(image_out)
os.makedirs(annotation_xml_out)

images = dict()
skip = False
points = ""
pt = []
f = open(annotation_out + os.sep + 'trainval.txt', 'w')
for root, dirs, files in os.walk(input_path):
    for filesimg in fnmatch.filter(files, "*.jpg"):
        path_to_file = os.path.join(root, filesimg)
        if not skip:
            with Image.open(path_to_file) as img:
                width, height = img.size
                img.save(os.path.join(image_out, filesimg))
                images[filesimg[:-4]] = {"width": width, "height": height}
    for files in fnmatch.filter(files, "*.xml"):
        print(files)
        print(root)
        path_to_file = os.path.join(root, files)
        f.write(str(files[:-4]) + '\n')
        if images.get(files[:-4]) is None:
            continue

        rootTree = ET.Element('annotation')
        filename = ET.SubElement(rootTree, "filename")
        filename.text = files[:-3] + "jpg"
        size = ET.SubElement(rootTree, "size")
        width = ET.SubElement(size, "width")
        width.text = str(images[files[:-4]].get("width"))
        height = ET.SubElement(size, "height")
        height.text = str(images[files[:-4]].get("height"))
        depth = ET.SubElement(size, "depth")
        depth.text = str(3)
        segmented = ET.SubElement(rootTree, "segmented")
        segmented.text = str(0)

        currentTree = ET.parse(path_to_file).iterfind("table")
        for child in currentTree:
            for subchild in child:
                #print(subchild.tag, subchild.attrib)
                if subchild.tag == "Coords":
                    points = subchild.attrib.get('points')

                    print(points)
                    list_points = points.split(" ")
                    print(points.split(" "))
                    xmax_ = 0
                    ymax_ = 0
                    xmin_ = 0
                    ymin_ = 0
                    pt = []

                    for i in range(4):
                        pt.append(list_points[i].split(","))
                        print(pt[i])
                        xmin_ = int(pt[0][0])
                        ymin_ = int(pt[0][1])
                        if int(pt[i][0]) > xmax_:
                            xmax_ = int(pt[i][0])
                        elif int(pt[i][0]) < xmin_:
                            xmin_ = int(pt[i][0])

                        if int(pt[i][1]) > ymax_:
                            ymax_ = int(pt[i][1])
                        elif int(pt[i][1]) < ymin_:
                            ymin_ = int(pt[i][1])
                    print("object - ", xmax_, " ", ymax_, " ", xmin_, " ", ymin_)
                    object = ET.SubElement(rootTree, "object")
                    name = ET.SubElement(object, "name")
                    name.text = "table"
                    bndbox = ET.SubElement(object, "bndbox")
                    xmin = ET.SubElement(bndbox, "xmin")
                    xmin.text = str(xmin_)
                    ymin = ET.SubElement(bndbox, "ymin")
                    ymin.text = str(ymin_)
                    xmax = ET.SubElement(bndbox, "xmax")
                    xmax.text = str(xmax_)
                    ymax = ET.SubElement(bndbox, "ymax")
                    ymax.text = str(ymax_)
        ElementTree(rootTree).write(open(os.path.join(annotation_xml_out, files), 'w'), encoding='unicode')
f.close()

