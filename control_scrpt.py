import os
import shutil
import subprocess
import xml.etree.ElementTree as ET
import copy
import configparser
from termcolor import colored
from sys import argv
import sys
import re

try:
    from transform_data import *
except ImportError:
    sys.path.insert(1, os.path.curdir)
    from transform_data import *

_debug = 0
_copy_suffix = 1
_skip_tun = 0
_skip_transform = 0
_skip_data = 0
_slash = os.sep
_train = 0

try:
    param1 = argv[1]
    if param1 == "-d":
        _debug = 1
except IndexError:
    print('-r')


def create_config(path_config):
    """
    Create a config file
    """
    config = configparser.ConfigParser()
    config.add_section("settings")
    config.set("settings", "train", "no")

    config.add_section("datasets")
    config.set("datasets", "output_path", "")
    config.set("datasets", "local_path", "")

    config.add_section("data_name")
    config.set("data_name", "name", "")
    config.set("data_name", "path_to_dataset", "")
    config.set("data_name", "script_to_convert", "")
    config.set("data_name", "enabled", "true")

    config.add_section("image_transform")
    config.set("image_transform", "script_to_transform", "")

    config.add_section("tuning_image")
    config.set("tuning_image", "script_to_tuning", "")

    config.add_section("records")
    config.set("records", "script_to_create_tf_records", "")
    config.set("records", "path_to_output", "")
    config.set("records", "path_to_label_map", "")

    with open(path_config, "w") as config_file:
        config.write(config_file)
        print(colored(" File " + path_config + " was created!", "blue"))


def replace_string(str):
    if re.findall(regex_out, str):
        return re.sub(regex_out, output_dir, str, count=0)
    elif re.findall(regex_loc, str):
        return  re.sub(regex_loc, local_dir, str, count=0)
    else:
        return str


def error_message(error_type, text, text2, text3):
    if error_type == 0:
        print(colored('ERROR! File ' + text + ' not found!', 'red', attrs=['reverse', 'bold']))
    elif error_type == 3:
        print(colored('ERROR! Process ' + text + ' finished with exit code ' + str(text2), 'red',
                      attrs=['reverse', 'bold']))
        raise SystemExit(3)
    elif error_type == 2:
        print(colored('ERROR! Folder ' + text + ' not found!', 'red', attrs=['reverse', 'bold']))
        print(colored(
            "Proposal: Enter the correct path ('" + text2 + "') in the [" + text3 + "] section of the config.ini file.",
            'yellow'))
        raise SystemExit(2)
    elif error_type == 1:
        print(colored('ERROR! Script ' + text + ' not found!', 'red', attrs=['reverse', 'bold']))
        print(colored(
            "Proposal: Enter the correct path ('" + text2 + "') in the [" + text3 + "] section of the config.ini file.",
            'yellow'))
        raise SystemExit(1)
    elif error_type == 4:
        print(colored('ERROR! Module  ' + text + ' return -1', 'red', attrs=['reverse', 'bold']))
        raise SystemExit(1)


if __name__ == "__main__":
    print(colored('\n Starting the script', 'blue', attrs=['bold']) + '\n')
    path = "config.ini"
    regex_out = "{output_path}"
    regex_loc = "{local_path}"
    if sys.version_info[0] < 3:
        python_ver = "python3"
    else:
        python_ver = "python"

    if not os.path.exists(path):
        error_message(0, path, '', '')  # ERROR
        create_config(path)
    else:
        config = configparser.ConfigParser()
        config.read(path)
        if config.get("settings", 'train').upper() == 'NO':
            _train = 0
        elif config.get("settings", 'train').upper() == 'YES':
            _train = 1
        if _debug == 1:
            print(colored(' TRAIN - ' + str(_train), 'yellow'))

        print(colored(' - datasets -', 'blue'))
        output_dir = config.get("datasets", 'output_path')
        if not os.path.exists(output_dir):
            os.mkdir(output_dir)
        local_dir = config.get("datasets", 'local_path')
        if not os.path.exists(local_dir):
            os.mkdir(local_dir)

        annotations_path = os.path.join(local_dir, "annotations")
        xmls_path = os.path.join(annotations_path, "xmls")
        images_path = os.path.join(local_dir, "images")

        # if os.path.exists(annotations_path):
        #     shutil.rmtree(annotations_path)
        # if os.path.exists(images_path):
        #     shutil.rmtree(images_path)
        # if os.path.exists(xmls_path):
        #     shutil.rmtree(xmls_path)
        #
        # os.makedirs(images_path)
        # os.makedirs(annotations_path)
        # os.makedirs(xmls_path)

        if not os.path.exists(os.path.join(output_dir, "annotations")):
            os.mkdir(os.path.join(output_dir, "annotations"))
        if not os.path.exists(os.path.join(os.path.join(output_dir, "annotations"), "xmls")):
            os.mkdir(os.path.join(os.path.join(output_dir, "annotations"), "xmls"))
        if not os.path.exists(os.path.join(output_dir, "images")):
            os.mkdir(os.path.join(output_dir, "images"))

        if _debug == 1:
            print(colored(' annotations (local) - ' + xmls_path + ' -> ' + str(os.path.exists(xmls_path)), 'yellow'))
            print(colored(' annotations (output data) - ' + os.path.join(os.path.join(output_dir, "annotations"), "xmls") + ' -> ' + str(os.path.exists(os.path.join(os.path.join(output_dir, "annotations"), "xmls"))), 'yellow'))

        dataset_list = []
        for line in open(path, 'r'):
            res = re.findall(r"\[data_\w+", line)
            if res and config.get(res[0][1:], "enabled").upper() == "TRUE":
                dataset_list.append(res[0][1:])

        for dataset_name in dataset_list:
            print(colored("= " + config.get(dataset_name, 'name') + " =", 'blue'))
            script = config.get(dataset_name, 'script_to_convert')
            data_dir = config.get(dataset_name, 'path_to_dataset')
            enabled = config.get(dataset_name, "enabled")
            if enabled.upper() == "YES" or enabled.upper() == "TRUE":
                if os.path.exists(script) or script == "":
                    if script != "":
                        print(colored('Running script', 'blue'), colored(script, 'blue', attrs=['underline']) + '\n',
                              colored('-i ' + data_dir + ' -o ' + output_dir, 'blue') + '\n')
                        code = subprocess.call([python_ver, script, '-i' + data_dir, '-o' + output_dir, '', ''])
                        if code != 0:
                            error_message(3, script, code, '')
                    else:
                        print(colored(' -Skip (script_to_convert is empty)-', 'yellow') + '\n')
                        _skip_data += 1
                        print(os.path.exists(data_dir  + _slash + 'annotations' + _slash + 'xmls'))

                        try:
                           transform(data_dir, output_dir, 'annotations' + _slash + 'xmls', 'images', 2)
                        except RuntimeError:
                            error_message(4, 'transform', '', '')
                else:
                    error_message(1, script, 'script_to_convert. Enabled = false', dataset_name)  # ERROR
                if len(dataset_list) > 1:
                    print(dataset_list)
                    move_files(output_dir, _debug, xmls_path, images_path)
            else:
                print(colored(' -Skip (enabled = false)-', 'yellow') + '\n')
        if len(dataset_list) > 1:
            shutil.rmtree(output_dir  + _slash + 'annotations')
            shutil.rmtree(output_dir  + _slash + 'images')
            print(colored(' - Some data conversions -', 'blue'))
            try:
                transform(local_dir, output_dir, 'annotations' + _slash + 'xmls', 'images', 2)
            except RuntimeError:
                error_message(4, 'transform', '', '')
        
        print(colored(" - Image Transform - ", 'blue'))
        script = config.get('image_transform', 'script_to_transform')
        data_dir = replace_string(config.get("datasets", 'output_path'))
        if os.path.exists(script) or script == "":
            if script != "":
                print(colored('Running script', 'blue'), colored(script, 'blue', attrs=['underline']) + '\n',
                      colored('-i ' + data_dir + ' -o ' + output_dir, 'blue') + '\n')
                code = subprocess.call([python_ver, script, '-i' + data_dir, '-o' + output_dir])
                if code != 0:
                    error_message(3, script, code, '')
            else:
                print(colored(' -Skip-', 'yellow') + '\n')
                _skip_transform = 1
        else:
            error_message(1, script, 'script_to_transform', 'image-transform')  # ERROR

        print(colored(" - Tuning Image - ", 'blue'))
        script = config.get('tuning_image', 'script_to_tuning')
        data_dir = replace_string(config.get("datasets", 'output_path'))
        if os.path.exists(script) or script == "":
            if script != "":
                print(colored('Running script', 'blue'), colored(script, 'blue', attrs=['underline']) + '\n',
                      colored('--data_dir=' + data_dir + ' --output_dir=' + local_dir, 'blue') + '\n')
                code = subprocess.call([python_ver, script, '--data_dir=' + data_dir, '--output_dir=' + local_dir])
                if code != 0:
                    error_message(3, script, code, '')
            else:
                print(colored(' -Skip-', 'yellow') + '\n')
                _skip_tun = 1
        else:
            error_message(1, script, 'script_to_tuning', 'tuning-image')  # ERROR
        if _skip_tun != 1:

            if os.path.exists(os.path.join(output_dir, 'images')):
                shutil.rmtree(os.path.join(output_dir, 'images'))
            if os.path.exists(os.path.join(output_dir, 'annotations')):
                shutil.rmtree(os.path.join(output_dir, 'annotations'))

            print(colored(' - Some data conversions -', 'blue'))
            try:
                transform(local_dir, output_dir, 'annotations' + _slash + 'xmls', 'images', 2)
                # move_files(local_dir, _debug, xmls_path, images_path)
            except RuntimeError:
                error_message(4, 'transform', '', '')

        print(colored(' - delete excess data -'+output_dir, 'blue'))
        delete_excess(output_dir)

        print(colored(" - Create tfRecords - ", 'blue'))
        script = config.get('records', 'script_to_create_tf_records')
        data_dir = config.get('datasets', 'output_path')
        data_dir = data_dir.replace('\\r', '\\\\r')
        output_path = config.get('records', 'path_to_output')
        output_path = output_path.replace('\\r', '\\\\r')
        print(output_path)
        label_map_path = config.get('records', 'path_to_label_map')
        label_map_path = label_map_path.replace('\\r', '\\\\r')
        if os.path.exists(script) or script == "":
            if script != "":
                print(colored('Running script', 'blue'), colored(script, 'blue', attrs=['underline']) + '\n',
                      colored('--data_dir=' + data_dir + ' ' + '--output_dir=' + output_path + ' ' + '--label_map_path=' +
                              label_map_path, 'blue') + '\n')
                code = subprocess.call([python_ver, script, '--data_dir=' + data_dir, '--output_dir=' + output_path,
                                        '--label_map_path=' + label_map_path])
                if code != 0:
                    error_message(3, script, code, '')
            else:
                print(colored(' -Skip-', 'yellow') + '\n')
        else:
            error_message(1, script, 'script_to_create_tf_records', 'records')  # ERROR

        if os.path.exists(os.path.join(local_dir, 'images')):
            shutil.rmtree(os.path.join(local_dir, 'images'))
        if os.path.exists(os.path.join(local_dir, 'annotations')):
            shutil.rmtree(os.path.join(local_dir, 'annotations'))

        if _train == 1:
            script = config.get('train', 'script_to_train')
            train_dir = config.get('train', 'train_dir')
            pipeline_config_path = config.get('train', 'pipeline_config_path')
            print(colored(" - Training - ", 'blue'))
            os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'
            print(colored('Running script'+script + ' --logtostderr --train_dir='+train_dir+'--pipeline_config_path' +
                          pipeline_config_path, 'blue'))
            code = subprocess.call([python_ver, script, '--logtostderr', '--train_dir='+train_dir, '--pipeline_config_path' +
                             pipeline_config_path])
            if code != 0:
                error_message(3, script, code, '')

        print(colored('\n Script finished', 'blue', attrs=['bold']))
        print(colored("File's train.record, val.record were created", 'blue', attrs=['bold']))
