from PIL import Image, ImageDraw
import random

import json

w, h = 595, 842
shape = [(10, 10), (w - 10, h - 10)]
work_directory = "/home/vasily/PycharmProjects/TestTensor/data/SciTSR/train/chunk"

img = Image.new("RGB", (w, h))

img1 = ImageDraw.Draw(img)
img1.rectangle([0,0,w,h], fill ="#ffffff")
#img1.rectangle(shape, fill ="#ffff33", outline ="red")

f = open(work_directory + '/0704.2596v1.2.chunk', 'r')

minx = w
miny = h
maxx = 0
maxy = 0

chunks = json.load(f)['chunks']
for chunk in chunks:
    print(chunk["pos"][0])
    print(chunk["pos"][1])
    print(chunk["pos"][2])
    print(chunk["pos"][3])
    clr = random.randrange(000000, 256)
    img1.rectangle([chunk["pos"][0], h-chunk["pos"][2], chunk["pos"][1], h-chunk["pos"][3]], fill=clr)
    print("")
    if minx > chunk["pos"][0]:
        minx = chunk["pos"][0]
    if miny > chunk["pos"][2]:
        miny = chunk["pos"][2]

    if maxx < chunk["pos"][1]:
        maxx = chunk["pos"][1]
    if maxy < chunk["pos"][3]:
        maxy = chunk["pos"][3]
print(minx, miny, maxx, maxy)

img1.rectangle([minx, miny, maxx, maxy], outline="green")

img.show()

f.close()

