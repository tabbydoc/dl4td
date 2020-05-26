from PIL import Image, ImageDraw
from pdf2image import convert_from_path
import random
import os
import sys
import codecs
from pylatexenc.latex2text import LatexNodes2Text
import re
from datetime import datetime
from xml.etree.ElementTree import ElementTree
import xml.etree.ElementTree as ET
import shutil
import getopt
import time

import json

def delete_exc_char(text):
    for ch in ['_', ' ', ' ', '^', '\n', '*', '\'', '\\', '`', '\t']:
        if ch in text:
            text = text.replace(ch, "")
    return text


w, h = 595, 842
w_img, h_img = 1654, 2339
# shape = [(10, 10), (w - 10, h - 10)]
_mode = 'train'
data_out = "F:\\Proj\\Python\\Sctisr\\data\\LOCAL_dir_test____"
work_directory = "F:\\Proj\\Python\\Sctisr\\data\\SciTSR___"
debug = False
_noImage = True

try:
    opts, args = getopt.getopt(sys.argv[1:], "hi:o:m:d", ["input_folder=", "output_folder=, mode="])
    # print(os.path.isdir(input_folder))
except getopt.GetoptError:
    print('test.py -i <input folder> -o <output folder> -m <test or train> -d (for debug)')
    sys.exit(2)
for opt, arg in opts:
    if opt == '-h':
        print('test.py -i <input folder> -o <output folder>')
        sys.exit()
    elif opt == '-d':
        debug = True
        _noImage = False
    elif opt in ("-i", "--i"):
        work_directory = arg
    elif opt in ("-m", "--m"):
        _mode = arg
    elif opt in ("-o", "--o"):
        data_out = arg

work_directory_pdf = os.path.join(work_directory, _mode, 'pdf')
work_directory_chunk = os.path.join(work_directory, _mode, 'chunk')
work_directory_structure = os.path.join(work_directory, _mode, 'structure')

print(work_directory_pdf)

annotation_out = os.path.join(data_out, "annotations")
annotation_xml_out = os.path.join(annotation_out, "xml")
image_out = os.path.join(data_out, "images")

if os.path.exists(annotation_out):
    shutil.rmtree(annotation_out)
if os.path.exists(annotation_xml_out):
    shutil.rmtree(annotation_xml_out)
if os.path.exists(image_out):
    shutil.rmtree(image_out)

os.makedirs(annotation_out)
os.makedirs(image_out)
os.makedirs(annotation_xml_out)

trainval = open(annotation_out + os.sep + 'trainval.txt', 'w')

skip_file_list = ['']

# max_step = 3000
max_step = 15000
step = 0
shift = 14
# min_step = 11990
min_step = 0

texx = 'γ ∗  \nb (dB) bf b (γ ∗  \nb )/γ ∗  \nb'
texx = delete_exc_char(texx).encode('ascii', errors='ignore')
print(texx)
tex = LatexNodes2Text().latex_to_text('$b f_b(\\gamma_b^*)/ \\gamma_b^*$').replace('_', '')
tex = delete_exc_char(tex).encode('ascii', errors='ignore')
# tex = 'Ω(n2logn)'.encode('ascii', errors='ignore')
print(str(tex).replace(' ', ''))
if tex == texx:
    print('y')
else:
    print('no')

start_time = datetime.now()
ignore_list = []

ignore_file = open('ignore.list', 'r')
for line in ignore_file:
    ignore_list.append(line.replace('\n', ''))
ignore_file.close()

# sys.exit(0)
for root, dirs, files in os.walk(work_directory_pdf):
    for file in files:
        if file in skip_file_list:
            continue
        step += 1
        if min_step > step:
            continue
        pages = convert_from_path(os.path.join(work_directory_pdf, file))
        print(file)
        pages[0].save(data_out + "\\images\\" + file[:-4] + ".jpeg", 'JPEG')

        if not _noImage:
            image = os.path.join(data_out, "images", file[:-4] + ".jpeg")
            print(image)
            img = Image.open(image)

            img1 = ImageDraw.Draw(img)
        chun = codecs.open(work_directory_chunk + '\\' + file[:-4] + '.chunk', 'r', encoding='utf-8')
        struct = codecs.open(work_directory_structure + '\\' + file[:-4] + '.json', 'r', encoding='utf-8')

        trainval.write(str(file[:-4]) + '\n')

        log = open('F:\\Proj\\Python\\Sctisr\\data\\logs_test\\' + file[:-4] + '.txt', 'w')
        log.write(file + '\n')
        minx = w_img
        miny = h_img
        maxx = 0
        maxy = 0
        skip = False
        if debug:
            log.write(str(chun) + '\n')
            # print(chun)

        chunks = json.load(chun)['chunks']
        structures = json.load(struct)['cells']

        if len(chunks) == len(structures) and not skip:
            if debug:
                print('skip')
            log.write('= skip; len(chunk){' + str(len(chunks)) + '} == len(structures){' + str(len(structures)) + '}')
            skip = True
        if not skip:
            # print(file, ' =?= ', line[:-1])
            for i in range(len(ignore_list)):
                if file in ignore_list[i]:
                    skip = True
                    print('skip')
                    log.write('= skip; In ignore list')
                    ignore_list.pop(i)
                    break

        rootTree = ET.Element('annotation')
        filename = ET.SubElement(rootTree, "filename")
        filename.text = str(file[:-3]) + "jpg"
        size = ET.SubElement(rootTree, "size")
        width = ET.SubElement(size, "width")
        width.text = str(w_img)
        height = ET.SubElement(size, "height")
        height.text = str(h_img)
        depth = ET.SubElement(size, "depth")
        depth.text = str(3)
        segmented = ET.SubElement(rootTree, "segmented")
        segmented.text = str(0)

        for chunk in chunks:
            if debug:
                log.write(str(chunk["pos"][0]) + '\n')
                log.write(str(chunk["pos"][1]) + '\n')
                log.write(str(chunk["pos"][2]) + '\n')
                log.write(str(chunk["pos"][3]) + '\n')
                log.write(str(LatexNodes2Text().latex_to_text(chunk["text"]).encode('utf-8')) + '\n')
                """
                print(chunk["pos"][0])
                print(chunk["pos"][1])
                print(chunk["pos"][2])
                print(chunk["pos"][3])
                print(LatexNodes2Text().latex_to_text(chunk["text"]))
                """
            if not _noImage:
                clr = random.randrange(0, 256)

                img1.rectangle(
                    [chunk["pos"][0] * (w_img / w), h_img - chunk["pos"][2] * (h_img / h), chunk["pos"][1] * (w_img / w),
                     h_img - chunk["pos"][3] * (h_img / h)], outline=clr)
            # print("")

            find = False
            if not skip:
                for i in range(len(structures)):
                    st = structures[i]
                    str1_ = chunk["text"].replace('’', '').replace('−', '-').replace('ﬁ', 'fi').replace('ﬃ',
                                                                                                        'ffi').replace(
                        'ﬀ', 'ff').replace('〈', '(').replace('〉', ')')
                    for j in range(20, 2, -1):
                        if re.findall(r'\\parbox{.{' + str(j) + '}}', st["tex"]):
                            st["tex"] = re.sub(r'\\parbox{.{' + str(j) + '}}', '', st["tex"])
                        elif re.findall(r'\\parbox\[.{' + str(j) + '}}', st["tex"]):
                            st["tex"] = re.sub(r'\\parbox\[.{' + str(j) + '}}', '', st["tex"])
                    if re.findall(r'\\mbox', st["tex"]):
                        st["tex"] = re.sub(r'\\mbox', '', st["tex"])
                    if re.findall(r'\\arg', st["tex"]):
                        st["tex"] = re.sub(r'\\arg', 'arg', st["tex"])
                    if re.findall(r'\\Pr', st["tex"]):
                        st["tex"] = re.sub(r'\\Pr', 'Pr', st["tex"])
                    if re.findall(r'{\\char\'134}', st["tex"]):
                        st["tex"] = re.sub(r'{\\char\'134}', '', st["tex"])
                    for jj in range(20, 6, -1):
                        if re.findall(r'\\rule{.{' + str(jj) + '}}', st["tex"]):
                            st["tex"] = re.sub(r'\\rule{.{' + str(jj) + '}}', '', st["tex"])
                        if re.findall(r'\\rule\[.{' + str(jj) + '}}', st["tex"]):
                            st["tex"] = re.sub(r'\\rule\[.{' + str(jj) + '}}', '', st["tex"])
                    for jjj in range(20, 6, -1):
                        if re.findall(r'\\raisebox{.{' + str(jjj) + '}]', st["tex"]):
                            st["tex"] = re.sub(r'\\raisebox{.{' + str(jjj) + '}]', '', st["tex"])
                    for jjj in range(20, 5, -1):
                        if re.findall(r'\\makebox\[.{' + str(jjj) + '}]', st["tex"]):
                            st["tex"] = re.sub(r'\\makebox\[.{' + str(jjj) + '}]', '', st["tex"])

                    str2_ = LatexNodes2Text().latex_to_text(st["tex"]).replace('’', '').replace('<ref>', '??').replace(
                        '〉', ')')
                    # str1 = b(str1)
                    str1 = delete_exc_char(str1_).encode('ascii', errors='ignore')
                    str2 = delete_exc_char(str2_).encode('ascii', errors='ignore')
                    if debug:
                        log.write(str(str1) + ' ?= ' + str(str2) + '\n')
                        # print(str1, ' ?= ', str2)

                    # if str2 != '' and (str1 == str2 or re.findall(str2, str1)):
                    if str2 != b'' and (str1 == str2):
                        find = True
                        structures.pop(i)
                        if debug:
                            # print('YEs')
                            log.write('YEs' + '\n')
                        break
                    elif chunk == chunks[len(chunks) - 1] and len(chunk) > 1 and (str2 != b'' and (str1[:-1] == str2)):
                        find = True
                        structures.pop(i)
                        if debug:
                            # print('YEs')
                            log.write('YEs' + '\n')
                        break
                    elif (str1 == b'' and str2 == b'') and (str1_ == str2_):
                        find = True
                        structures.pop(i)
                        if debug:
                            # print('YEs')
                            log.write('YEs' + '\n')
                        break
                    if debug:
                        # print('NO')
                        log.write('NO' + '\n')
            if find or skip:
                if minx > chunk["pos"][0]:
                    minx = chunk["pos"][0]
                if miny > chunk["pos"][2]:
                    miny = chunk["pos"][2]

                if maxx < chunk["pos"][1]:
                    maxx = chunk["pos"][1]
                if maxy < chunk["pos"][3]:
                    maxy = chunk["pos"][3]
        if debug:
            print("xmin:", minx * (w_img / w), "ymin:", h_img - miny * (h_img / h), "xmax:", maxx * (w_img / w), "ymax:",
              h_img - maxy * (h_img / h))
            print('STEP: ', step)

        object = ET.SubElement(rootTree, "object")
        name = ET.SubElement(object, "name")
        name.text = "table"
        bndbox = ET.SubElement(object, "bndbox")
        xmin = ET.SubElement(bndbox, "xmin")
        xmin.text = str(int(minx * (w_img / w) - shift))
        ymin = ET.SubElement(bndbox, "ymin")
        ymin.text = str(int(h_img - maxy * (h_img / h) - shift))
        xmax = ET.SubElement(bndbox, "xmax")
        if maxx * (w_img / w) + shift > w_img:
            xmax.text = str(w_img)
        else:
            xmax.text = str(int(maxx * (w_img / w) + shift))
        ymax = ET.SubElement(bndbox, "ymax")
        if h_img - miny * (h_img / h) + shift > h_img:
            ymax.text = str(h_img)
        else:
            ymax.text = str(int(h_img - miny * (h_img / h) + shift))

        ElementTree(rootTree).write(open(os.path.join(annotation_xml_out, file[:-3] + "xml"), 'w'), encoding='unicode')

        if not _noImage:
            img1.rectangle([minx * (w_img / w) - shift, h_img - miny * (h_img / h) + shift, maxx * (w_img / w) + shift,
                            h_img - maxy * (h_img / h) - shift], outline="green", width=7)
        # img.show()
        chun.close()
        struct.close()
        if not _noImage:
            img.save(data_out + "\\annotations\\" + file[:-4] + ".jpeg")

        if debug:
            # print('')
            print('=' * 15)
            # print('')
        if step >= max_step:
            break
    if step >= max_step:
        break

trainval.close()
print('= ВРЕМЯ РАБОТЫ : ', datetime.now() - start_time)

sys.exit(0)

