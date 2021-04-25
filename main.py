import os
import subprocess
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
_skip_this = 0

try:
    param1 = argv[1]
    if param1 == "-d":
        _debug = 1
except IndexError:
    print('-r')


# Function to create a config.ini file
def create_config(path_config):
    config_f = configparser.ConfigParser()

    config_f.add_section("datasets")
    config_f.set("datasets", "output_path", "")
    config_f.set("datasets", "local_path", "")

    config_f.add_section("data_name")
    config_f.set("data_name", "name", "")
    config_f.set("data_name", "path_to_dataset", "")
    config_f.set("data_name", "script_to_convert", "")
    config_f.set("data_name", "enabled", "true")

    config_f.add_section("image_transform")
    config_f.set("image_transform", "script_to_transform", "")

    config_f.add_section("tuning_image")
    config_f.set("tuning_image", "script_to_tuning", "")

    config_f.add_section("records")
    config_f.set("records", "script_to_create_tf_records", "")
    config_f.set("records", "path_to_output", "")
    config_f.set("records", "path_to_label_map", "")

    with open(path_config, "w") as config_file:
        config_f.write(config_file)
        print(colored(" File " + path_config + " was created!", "blue"))


# Replacing the words {output_path} and {local_path} with the appropriate path.
def replace_string(string):
    if re.findall(regex_out, string):
        return re.sub(regex_out, output_dir, string, count=0)
    elif re.findall(regex_loc, string):
        return re.sub(regex_loc, local_dir, string, count=0)
    return string


# Error call function
def error_message(error_type, text):
    if error_type == 0:
        print(colored('ERROR! File ' + text[0] + ' not found!', 'red', attrs=['reverse', 'bold']))
    elif error_type == 3:
        print(colored('ERROR! Process ' + text[0] + ' finished with exit code ' + str(text[1]), 'red',
                      attrs=['reverse', 'bold']))
        raise SystemExit(3)
    elif error_type == 2:
        print(colored('ERROR! Folder ' + text[0] + ' not found!', 'red', attrs=['reverse', 'bold']))
        print(colored(
            "Proposal: Enter the correct path ('" + text[1] + "') in the [" + text[2] + "] section of the config.ini "
                                                                                        "file.", 'yellow'))
        raise SystemExit(2)
    elif error_type == 1:
        print(colored('ERROR! Script ' + text[0] + ' not found!', 'red', attrs=['reverse', 'bold']))
        print(colored(
            "Proposal: Enter the correct path ('" + text[1] + "') in the [" + text[2] + "] section of the config.ini "
                                                                                        "file.", 'yellow'))
        raise SystemExit(1)
    elif error_type == 4:
        print(colored('ERROR! Module  ' + text[0] + ' return -1', 'red', attrs=['reverse', 'bold']))
        raise SystemExit(4)


if __name__ == "__main__":
    print(colored('\n Starting the script', 'blue', attrs=['bold']) + '\n')
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "config.ini")
    regex_out = "{output_path}"
    regex_loc = "{local_path}"
    if sys.version_info[0] < 3:
        python_ver = "python3"
    else:
        python_ver = "python"

    if not os.path.exists(path):
        error_message(0, [path])  # ERROR
        create_config(path)
    else:
        # Reading parameters from a file and preparing the output directory.
        config = configparser.ConfigParser()
        config.read(path)

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

        if os.path.exists(annotations_path):
            shutil.rmtree(annotations_path)
        if os.path.exists(images_path):
            shutil.rmtree(images_path)
        if os.path.exists(xmls_path):
            shutil.rmtree(xmls_path)
        remove_inside(output_dir)

        os.makedirs(images_path)
        os.makedirs(annotations_path)
        os.makedirs(xmls_path)

        if not os.path.exists(os.path.join(output_dir, "annotations")):
            os.mkdir(os.path.join(output_dir, "annotations"))
        if not os.path.exists(os.path.join(output_dir, "annotations", "xmls")):
            os.mkdir(os.path.join(output_dir, "annotations", "xmls"))
        if not os.path.exists(os.path.join(output_dir, "images")):
            os.mkdir(os.path.join(output_dir, "images"))

        if _debug == 1:
            print(colored(' annotations (local) - ' + xmls_path + ' -> ' + str(os.path.exists(xmls_path)), 'yellow'))
            print(colored(' annotations (output data) - ' + os.path.join(output_dir, "annotations", "xmls") + ' -> ' +
                          str(os.path.exists(os.path.join(output_dir, "annotations", "xmls"))), 'yellow'))

        # Read all datasets from the config.ini file
        dataset_list = []
        for line in open(path, 'r'):
            res = re.findall(r"\[data_\w+", line)
            if res and config.get(res[0][1:], "enabled").upper() == "TRUE":
                dataset_list.append(res[0][1:])

        # Run dataset conversion
        for dataset_name in dataset_list:
            print(colored("= " + config.get(dataset_name, 'name') + " =", 'blue'))
            _skip_this = 0
            script = config.get(dataset_name, 'script_to_convert')
            data_dir = config.get(dataset_name, 'path_to_dataset')
            if not os.path.exists(data_dir):
                error_message(2, [data_dir, "path_to_dataset", dataset_name])
            enabled = config.get(dataset_name, "enabled")
            if enabled.upper() == "YES" or enabled.upper() == "TRUE":
                if os.path.exists(script) or script == "":
                    if script != "":
                        print(colored('Running script', 'blue'), colored(script, 'blue', attrs=['underline']) + '\n',
                              colored('-i ' + data_dir + ' -o ' + output_dir, 'blue') + '\n')
                        code = subprocess.call([python_ver, script, '-i' + data_dir, '-o' + output_dir, '', ''])
                        if code != 0:
                            error_message(3, [script, code])
                    else:
                        print(colored(' -Skip (script_to_convert is empty)-', 'yellow') + '\n')
                        _skip_data += 1
                        _skip_this = 1

                        remove_inside(output_dir)
                        try:
                            if len(dataset_list) > 1:
                                move_files(data_dir, _debug, xmls_path, images_path)
                            else:
                                transform(data_dir, output_dir, 'annotations' + _slash + 'xmls', 'images', 2)
                        except RuntimeError:
                            error_message(4, ['transform'])

                else:
                    error_message(1, [script, 'script_to_convert. Enabled = false', dataset_name])  # ERROR
                if len(dataset_list) > 1:
                    print(dataset_list)
                    if _skip_this == 0:
                        move_files(output_dir, _debug, xmls_path, images_path)
                    else:
                        _skip_this = 0
            else:
                print(colored(' -Skip (enabled = false)-', 'yellow') + '\n')
        if len(dataset_list) > 1:
            shutil.rmtree(os.path.join(output_dir, 'annotations'), ignore_errors=True)
            shutil.rmtree(os.path.join(output_dir, 'images'), ignore_errors=True)
            print(colored(' - Some data conversions -', 'blue'))
            try:
                transform(local_dir, output_dir, 'annotations' + _slash + 'xmls', 'images', 2)
            except RuntimeError:
                error_message(4, ['transform'])

        # Run image transforming
        print(colored(" - Image Transform - ", 'blue'))
        script = config.get('image_transform', 'script_to_transform')
        data_dir = replace_string(config.get("datasets", 'output_path'))
        if os.path.exists(script) or script == "":
            if script != "":
                print(colored('Running script', 'blue'), colored(script, 'blue', attrs=['underline']) + '\n',
                      colored('-i ' + data_dir + ' -o ' + output_dir, 'blue') + '\n')
                code = subprocess.call([python_ver, script, '-i' + data_dir, '-o' + output_dir])
                if code != 0:
                    error_message(3, [script, code])
            else:
                print(colored(' -Skip-', 'yellow') + '\n')
                _skip_transform = 1
        else:
            error_message(1, [script, 'script_to_transform', 'image-transform'])  # ERROR

        # Run data tuning
        print(colored(" - Tuning Image - ", 'blue'))
        script = config.get('tuning_image', 'script_to_tuning')
        data_dir = replace_string(config.get("datasets", 'output_path'))
        if os.path.exists(script) or script == "":
            if script != "":
                print(colored('Running script', 'blue'), colored(script, 'blue', attrs=['underline']) + '\n',
                      colored('--data_dir=' + data_dir + ' --output_dir=' + local_dir, 'blue') + '\n')
                code = subprocess.call([python_ver, script, '--data_dir=' + data_dir, '--output_dir=' + local_dir])
                if code != 0:
                    error_message(3, [script, code])
            else:
                print(colored(' -Skip-', 'yellow') + '\n')
                _skip_tun = 1
        else:
            error_message(1, [script, 'script_to_tuning', 'tuning-image'])  # ERROR
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
                error_message(4, ['transform'])

        print(colored(' - delete excess data -' + output_dir, 'blue'))
        delete_excess(output_dir)

        # Create TensorFlow record files
        print(colored(" - Create tfRecords - ", 'blue'))
        script = config.get('records', 'script_to_create_tf_records')
        data_dir = os.path.abspath(config.get('datasets', 'output_path'))
        output_path = os.path.abspath(config.get('records', 'path_to_output'))
        label_map_path = os.path.abspath(config.get('records', 'path_to_label_map'))
        if os.path.exists(script) or script == "":
            if script != "":
                print(colored('Running script', 'blue'), colored(script, 'blue', attrs=['underline']) + '\n',
                      colored(
                          '--data_dir=' + data_dir + ' ' + '--output_dir=' + output_path + ' ' + '--label_map_path=' +
                          label_map_path, 'blue') + '\n')
                code = subprocess.call([python_ver, script, '--data_dir=' + data_dir, '--output_dir=' + output_path,
                                        '--label_map_path=' + label_map_path])
                if code != 0:
                    error_message(3, [script, code])
            else:
                print(colored(' -Skip-', 'yellow') + '\n')
        else:
            error_message(1, [script, 'script_to_create_tf_records', 'records'])  # ERROR

        print(colored('\n Script finished', 'blue', attrs=['bold']))
        print(colored("File's train.record, val.record were created", 'blue', attrs=['bold']))
