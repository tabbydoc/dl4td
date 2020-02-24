from PIL import Image, ImageDraw
from pdf2image import convert_from_path
import random
import os
import sys
import codecs
from pylatexenc.latex2text import LatexNodes2Text
import re

import json


def b(text):
    for ch in ['\\','`','*','+','{','}','[',']','(',')','>','#','+','-','.','!','$','\'','?','^','|',',']:
        if ch in text:
            text = text.replace(ch,"\\"+ch)
    return text


def delete_exc_char(text):
    for ch in ['_', ' ', ' ', '^', '\n']:
        if ch in text:
            text = text.replace(ch,"")
    return text


w, h = 595, 842
w_img, h_img = 1654, 2339
# shape = [(10, 10), (w - 10, h - 10)]
work_directory = "D:\\Server\\PyCharm\\Project\\image_transform\\data\\SciTSR"
work_directory_pdf = os.path.join(work_directory, 'train', 'pdf')
work_directory_chunk = os.path.join(work_directory, 'train', 'chunk')
work_directory_structure = os.path.join(work_directory, 'train', 'structure')
data_out = "D:\\Server\\PyCharm\\Project\\image_transform\\data\\LOCAL3"

max_step = 12000
step = 0
shift = 8

texx = 'Ω(n2logn)'.encode('ascii', errors='ignore')
print(texx)
tex = LatexNodes2Text().latex_to_text('$\\lambda$').replace('_', '')
tex = 'Ω(n2logn)'.encode('ascii', errors='ignore')
print(str(tex).replace(' ', ''))
if tex == texx:
    print('y')
else:
    print('no')
debug = True


# sys.exit(0)
for root, dirs, files in os.walk(work_directory_pdf):
    for file in files:
        pages = convert_from_path(os.path.join(work_directory_pdf, file))
        print(file)
        pages[0].save(data_out + "\\images\\" + file[:-4] + ".jpeg", 'JPEG')
        step += 1

        image = os.path.join(data_out, "images", file[:-4] + ".jpeg")
        print(image)
        img = Image.open(image)

        img1 = ImageDraw.Draw(img)
        chun = codecs.open(work_directory_chunk + '\\' + file[:-4] + '.chunk', 'r', encoding='utf-8')
        struct = codecs.open(work_directory_structure + '\\' + file[:-4] + '.json', 'r', encoding='utf-8')

        log = open('D:\\Server\\PyCharm\\Project\\image_transform\\data\\logs\\'+file[:-4]+'.txt', 'w')
        log.write(file+'\n')
        minx = w_img
        miny = h_img
        maxx = 0
        maxy = 0
        if debug:
            log.write(str(chun)+'\n')
            # print(chun)

        chunks = json.load(chun)['chunks']
        structures = json.load(struct)['cells']
        for chunk in chunks:
            if debug:
                log.write(str(chunk["pos"][0])+'\n')
                log.write(str(chunk["pos"][1])+'\n')
                log.write(str(chunk["pos"][2])+'\n')
                log.write(str(chunk["pos"][3])+'\n')
                log.write(str(LatexNodes2Text().latex_to_text(chunk["text"]).encode('utf-8'))+'\n')
                """
                print(chunk["pos"][0])
                print(chunk["pos"][1])
                print(chunk["pos"][2])
                print(chunk["pos"][3])
                print(LatexNodes2Text().latex_to_text(chunk["text"]))
                """
            clr = random.randrange(0, 256)
            img1.rectangle(
                [chunk["pos"][0] * (w_img / w), h_img - chunk["pos"][2] * (h_img / h), chunk["pos"][1] * (w_img / w),
                 h_img - chunk["pos"][3] * (h_img / h)], outline=clr)
            # print("")

            find = False

            for st in structures:
                str1 = chunk["text"].replace('’', '\'').replace('−','-').replace('ﬁ', 'fi')
                str2 = LatexNodes2Text().latex_to_text(st["tex"]).replace('’', '\'').replace('<ref>', '??')
                # str1 = b(str1)
                str1 = delete_exc_char(str1).encode('ascii', errors='ignore')
                str2 = delete_exc_char(str2).encode('ascii', errors='ignore')
                if debug:
                    log.write(str(str1) + ' ?= ' + str(str2)+'\n')
                    # print(str1, ' ?= ', str2)

                # if str2 != '' and (str1 == str2 or re.findall(str2, str1)):
                if str2 != '' and (str1 == str2 or str1[:-1] == str2):
                        find = True
                        if debug:
                            #print('YEs')
                            log.write('YEs'+'\n')
                        break
                if debug:
                    #print('NO')
                    log.write('NO'+'\n')
            if find:
                if minx > chunk["pos"][0]:
                    minx = chunk["pos"][0]
                if miny > chunk["pos"][2]:
                    miny = chunk["pos"][2]

                if maxx < chunk["pos"][1]:
                    maxx = chunk["pos"][1]
                if maxy < chunk["pos"][3]:
                    maxy = chunk["pos"][3]
        print("xmin:", minx * (w_img / w), "ymin:", h_img - miny * (h_img / h), "xmax:", maxx * (w_img / w), "ymax:",
              h_img - maxy * (h_img / h))
        print('STEP: ', step)

        img1.rectangle([minx * (w_img / w) - shift, h_img - miny * (h_img / h) + shift, maxx * (w_img / w) + shift,
                        h_img - maxy * (h_img / h) - shift], outline="green", width=7)
        # img.show()
        chun.close()
        struct.close()
        img.save(data_out + "\\annotations\\" + file[:-4] + ".jpeg")

        if debug:
            # print('')
            print('='*15)
            # print('')
        if step >= max_step:
            break
    if step >= max_step:
        break


sys.exit(0)
# ............................................................. #

work_directory = "D:\\Server\\PyCharm\\Project\\image_transform\\data\\SciTSR"
work_directory_chunk = os.path.join(work_directory, "train\\chunk")
data_out = "D:\\Server\\PyCharm\\Project\\image_transform\\data\\OUT"
file = "0705.0450v1.8"
shift = 10

pages = convert_from_path(os.path.join(work_directory, "train\\pdf\\" + file + ".pdf"))
pages[0].save(data_out + "\\" + file + ".jpeg", 'JPEG')

img = Image.open(data_out + "\\" + file + ".jpeg")
# img = Image.new("RGBA", (w, h))

img1 = ImageDraw.Draw(img)
# img1.rectangle([0, 0, w * (w_img / w), h * (h_img / h)], fill="#ffffff")
# img1.rectangle(shape, fill ="#ffff33", outline ="red")


f = open(work_directory_chunk + '\\' + file + '.chunk', 'r')

minx = w_img
miny = h_img
maxx = 0
maxy = 0

chunks = json.load(f)['chunks']
for chunk in chunks:
    print(chunk["pos"][0])
    print(chunk["pos"][1])
    print(chunk["pos"][2])
    print(chunk["pos"][3])
    clr = random.randrange(000000, 256)
    img1.rectangle([chunk["pos"][0] * (w_img / w), h_img - chunk["pos"][2] * (h_img / h), chunk["pos"][1] * (w_img / w), h_img - chunk["pos"][3] * (h_img / h)], fill=clr)
    print("")
    if minx > chunk["pos"][0]:
        minx = chunk["pos"][0]
    if miny > chunk["pos"][2]:
        miny = chunk["pos"][2]

    if maxx < chunk["pos"][1]:
        maxx = chunk["pos"][1]
    if maxy < chunk["pos"][3]:
        maxy = chunk["pos"][3]
print("xmin:", minx * (w_img / w), "ymin:", h_img - miny * (h_img / h), "xmax:", maxx * (w_img / w), "ymax:", h_img - maxy * (h_img / h))

img1.rectangle([minx * (w_img / w) - shift, h_img - miny * (h_img / h) + shift, maxx * (w_img / w) + shift, h_img - maxy * (h_img / h) - shift], outline="green")
img.show()

f.close()

img.save("out.jpeg")
