# DL4TD
These scripts help to create DNN-models for table detection in image documents. They aim at reducing user efforts needed for DL preparation and configuration.

## Description of scripts
The `main.py` is script to automate data preparation for training ANN models
The script uses a special file `config.ini`. This file contains the script start-up parameters. This is necessary to simplify the launch of the script.

The "scripts" directory contains scripts for conversion datasets, image transform, augmentation data, create tf record.

The `icdar2017_to_pascalvoc` is script for conversion ICDAR2017 dataset to PASCALVOC dataset.  
 
The `icdar2019сtdar_to_pascalvoc` is script for conversion ICDAR2019cTDaR dataset to PASCALVOC dataset.

The `marmot_to_pascalvoc` is script for conversion Marmot dataset to PASCALVOC dataset.

The `unlv_to_pascalvoc` is script for conversion UNLV dataset to PASCALVOC dataset.

The `augmentation_data` is script for augmentation data. Augmentation of data occurs due to a change in the width and height of the images. By changing the width and height of the image, you can get 9 times more data. 

Figure 1:
![augmentation data example](https://zigorewslike.github.io/sourse/img_tun_transf_big.png)

------------
The `image_transform` is script for serial action. This script is first binarized (see Figure 2 (a)), then the image break down on the RGB channels and the "distanceTransform" function is used (see Figure 2 (b))

Figure 2:
![image_transform example](https://zigorewslike.github.io/sourse/binary_and_distance2.png)


## Installation
Python 3.5+ is needed. Install the necessary libraries.

```python
pip install -r requirements.txt
```

## How to use
Then, you need to specify all the parameters in the `config.ini` file and run `control.py` script. 

### Setup *Config.ini* file
`Config.ini` file is divided into sections. The first section is ‘‘datasets’’. 
```ini
    [datasets]
    output_path = <...>
    local_path = <...>
```
The *output_path* parameter stores the path where the converted data will be saved. The *local_path* parameter is the path to the directory where the temporary script files will be stored. This parameter is needed if there are several datasets and a script that converts one dataset into another re-creates the directories, thereby deleting the files that were in the *output_path* folder. The converted dataset will be copied to the temporary folder, files that have the same name will be renamed. 

------------
The following N sections store parameters for specific datasets, where N is the number of datasets.

```ini
    [data_name]
    name = <...>
    path_to_dataset = <...>
    script_to_convert = <...>
```
[data_name] is name of section (``name'' is the user-defined custom name.).
Example: 
```ini
    [datasets]
    output_path = data/out
    local_path = data/local
    
    [data_icdar2017]
    name = ICDAR 2017
    path_to_dataset = data/icdar2017
    script_to_convert = scripts/icdar2017_to_pascalvoc/main.py
    enabled = true
    
    [data_marmot]
    name = Marmot
    path_to_dataset = data/marmot
    script_to_convert = scripts/marmot_to_pascalvoc/main.py
    enabled = true
```
Inside the *data_name* section there are three parameters: *name*, *path_to_datasets*, *script_to_convert*. The *name* parameter is needed in order to display a message on the console exactly which data is converted (this parameter is necessary for the convenience of reading logs). The *path_to_datasets* parameter stores the path to dataset. The *script_to_convert* contains the path to the script that converts datasets. The *enabled* parameter indicates whether or not to use this dataset.

The next section is *image_transform*. This section contains options for image conversion.
```ini
    [image_transform]
    script_to_transform = <...> 
```
The path to the script that converts the image is written to the *script_to_transform* parameter.
Example: 
```ini
    [image-transform]
    script_to_transform = scripts/image_transform/main.py
```
------------
The *tuning_transform* section contains parameters for running a script that will perform data augmentation.
```ini
    [tuning_transform]
    script_to_tuning = <...>
```
In the parameter *script_to_tuning* the script is specified that will make the data augmentation.
Example: 
```ini
    [tuning_transform]
    script_to_tuning = scripts/augmentation_data/main.py
```
------------
The last section is *records*. This section contains the parameters for running the script that creates input files of the record type.
```ini
    [records]
    script_to_create_tf_records = <...>
    path_to_output = <...>
    path_to_label_map = <...>
```
The parameter *path_to_output* stores the path to the folder where to save the record type files. The *path_to_label_map* stores the path to *label_map.pbtxt* file. The *label_map.pbtxt* file contains the name and ID of the classes,it is necessary to learn to recognize.
Example: 
```ini
    [records]
    script_to_create_tf_records = scripts/create_table_tf_record/create_tf_record.py
    path_to_output = data/out/rec
    path_to_label_map = data/label_map.pbtxt
```

------------
It is also possible to use links to parameters *output_path*, *local_path*. To do this, write the parameters in curly braces. 
For example:
```ini
    [datasets]
    output_path = data/out
    local_path = local/temp
    
    ...
    
    [records]
    script_to_create_tf_records = scripts/create_table_tf_record/create_tf_record.py
    path_to_output = {output_path}
    path_to_label_map = data/label_map.pbtxt
```
The script will automatically replace the references to the path specified in the specified parameters.
