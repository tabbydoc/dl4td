import sys
import os

input_folder = 'D:/WORK'
cout_files = 0
vis = 0
folder_ann = 'annotations/xml'
folder_img = 'images'

Files = os.listdir(input_folder)

for xml_file in Files:
    if xml_file.endswith('.jpeg'):
        cout_files += 1
        ann_path_in = os.path.join(input_folder, folder_ann + '/' + xml_file)
        if vis == 2:
            print("Файл xml на входе - " + ann_path_in)
        ann_path_out = os.path.join(xml_folder, xml_file)
        if vis == 2:
            print("Файл xml скопирован - " + ann_path_out)
        file_name = xml_file[:-4]
        if vis == 2:
            print("Название файла - " + str(file_name))
        f.write(str(file_name) + '\n')

        img_path_in = os.path.join(input_folder, folder_img + '/' + file_name + '.jpeg')
        if vis == 2:
            print("Файл jpeg на входе - " + img_path_in)
        img_path_out = os.path.join(img_folder, file_name + '.jpeg')
        if vis == 2:
            print("Файл jpeg скопирован - " + img_path_out)
        #shutil.copyfile(ann_path_in, ann_path_out)
        #shutil.copyfile(img_path_in, img_path_out)
        if vis == 2 or vis == 1:
            print("файл %s (xml и jpeg) скопирован!" % file_name)

        if vis == 2:
            print("==================")
