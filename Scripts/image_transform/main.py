import sys
import os
import fnmatch
import getopt
import cv2
from PIL import Image
#import curses

#myscreen = curses.initscr()
#myscreen.border(0)

def main(argv):
    input_folder = ''
    output_folder = ''

    try:
        opts, args = getopt.getopt(argv, "hi:o:", ["input_folder=", "output_folder="])
    except getopt.GetoptError:
        print('image_transform.py -i <input folder> -o <output folder>')
        sys.exit(2)

    for opt, arg in opts:
        if opt == '-h':
            print('image_transform.py -i <input folder> -o <output folder>')
            sys.exit()
        elif opt in ("-i", "--i"):
            input_folder = arg
        elif opt in ("-o", "--o"):
            output_folder = os.path.join(arg, 'images')

    is_dir = os.path.isdir(input_folder)

    if not is_dir:
        raise Exception(input_folder, "- It is not a folder")

    print("= Begin transform =")
    for root, directories, files in os.walk(input_folder):
        for file_name in fnmatch.filter(files, "*.jpeg"):
            path = os.path.join(root, file_name)
            name = os.path.splitext(os.path.split(path)[1])[0]
            save_path = os.path.join(output_folder, name + ".jpeg")
            img = cv2.imread(path)
            bimage = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
            image = transform_image(bimage)
            cv2.imwrite(save_path, image)


def rgb_to_binary(img):
    gray_img = img.convert("L")
    binary_img = gray_img.point(lambda x: 0 if x < 128 else 255, "1")
    return binary_img


def ndarray_to_image(data):
    return Image.fromarray(data.astype("uint8"))


def transform_image(img):
    b = cv2.distanceTransform(img, distanceType=cv2.DIST_L2, maskSize=5)
    g = cv2.distanceTransform(img, distanceType=cv2.DIST_L1, maskSize=5)
    r = cv2.distanceTransform(img, distanceType=cv2.DIST_C, maskSize=5)
    img = cv2.merge((b, g, r))
    return img

    # img_blur = img.filter(ImageFilter.EMBOSS)
    # img_gaus = img_blur.filter(ImageFilter.GaussianBlur())
    # return img_blur


if __name__ == "__main__":
    main(sys.argv[1:])
