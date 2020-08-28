# Create_table_tf_record

------

Tensor Flow Object Detection API requires a dataset of images and ground truth boxes, packaged as TFRecords of TFExamples. To create such a dataset for table detection, we use the `create_tf_record.py` script from this framework. It can convert data from Pascal VOC format to TF Records (TensorFlow Records). This script derives `train.record` and `val.record` files. The first one is required to train a model, and the second one is used for validation.
