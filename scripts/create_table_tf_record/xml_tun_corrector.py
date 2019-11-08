import os
import cv2
import tensorflow as tf
import xml.etree.ElementTree as ET
import copy
import shutil


flags = tf.app.flags
flags.DEFINE_string('data_dir', '', 'Root directory to raw pages dataset.')
flags.DEFINE_string('output_dir', '', 'Path to output directory.')
FLAGS = flags.FLAGS


def main(_):

    data_dir = FLAGS.data_dir
    #image_dir = os.path.join(data_dir, 'images')
    annotations_dir = os.path.join(data_dir, 'annotations')
    examples_path = os.path.join(annotations_dir, 'trainval.txt')
    xmls_path = os.path.join(annotations_dir, 'xmls')

    output_path = FLAGS.output_dir
    out_annotations_dir = os.path.join(output_path, 'annotations')
    #out_image_dir = os.path.join(output_path, 'images')
    o_examples_path = os.path.join(output_path, 'trainval.txt')
    out_xmls_path = os.path.join(out_annotations_dir, 'xmls')

    if os.path.exists(out_annotations_dir):
        shutil.rmtree(out_annotations_dir)
    #if os.path.exists(out_image_dir):
    #    shutil.rmtree(out_image_dir)
    if os.path.exists(out_xmls_path):
        shutil.rmtree(out_xmls_path)

    os.makedirs(out_annotations_dir)
    #os.makedirs(out_image_dir)
    os.makedirs(out_xmls_path)

    train_val = open(examples_path, 'r')
    files = train_val.read().splitlines()

    o_examples = open(o_examples_path, 'w')

    scales = [(1, 1),
              (0.8, 1), (0.9, 1), (1.1, 1), (1.2, 1),
              (1, 0.8), (1, 0.9), (1, 1.1), (1, 1.2)]

    for file in files:

        print(file)

        #image_name = os.path.join(image_dir, file + '.jpeg')
        #image = cv2.imread(image_name)
        #new_image_name = os.path.join(out_image_dir, file + '.jpeg')
        #cv2.imwrite(new_image_name, image)

        annotation_name = os.path.join(xmls_path, file + '.xml')
        xml_tree = ET.parse(annotation_name)

        count = 0

        for scale in scales:

            suffix = 'tuned_' + str(count)
            #o_examples.write(file + suffix + '\n')

            #resize_image = cv2.resize(image, None, fx=scale[0], fy=scale[1])
            #new_image_name = os.path.join(out_image_dir, file + suffix + '.jpeg')
            #cv2.imwrite(new_image_name, resize_image)

        new_xml_tree = copy.deepcopy(xml_tree)


        filename_img = new_xml_tree.find('filename')
        filename_img.text = file + '.jpeg'


        new_annotation_name = os.path.join(out_xmls_path, file + '.xml')
        new_xml_tree.write(new_annotation_name)

        count += 1


if __name__ == '__main__':
    tf.app.run()