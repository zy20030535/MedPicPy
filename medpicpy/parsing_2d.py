# contains files for doing 2d segmentation reading
import pandas as pd
import numpy as np
import cv2
import glob
from pathlib import Path
from .io import read
from sklearn.preprocessing import LabelEncoder, LabelBinarizer

# opt args to add
#   - resize keeps aspect ratio?

def read_images_from_csv(dataframe, image_name_column, image_dir_path, output_shape):
    array_length = len(dataframe[image_name_column])
    array_shape = (array_length,) + output_shape    # needs to be a tuple to concatenate
    image_array = np.zeros(array_shape)

    for i in range(0, array_length):
        image_name = dataframe[image_name_column][i]
        image_path = image_dir_path + image_name
        image = read.load_image(image_path)
        resized = cv2.resize(image, output_shape)
        image_array[i] = resized

    return image_array

# other encoding is categorical with labelencoder, or none and it just returns the series
def read_classes_from_csv(dataframe, classes_column, encoding='one_hot'):
    classes = None
    encoder = None
    class_column = dataframe[classes_column]

    #check for nans
    if class_column.isnull().values.any():
        print("Warning: csv contains NaN (not a number values).")
        class_column.fillna("nan", inplace=True)

    if encoding == "one_hot":
        encoder = LabelBinarizer()
    

    classes = encoder.fit_transform(class_column)
    print("{} Classes found: {}".format(len(encoder.classes_),encoder.classes_))
    
    return classes
    
def read_bounding_boxes_from_csv(
    dataframe, 
    centre_x_column, centre_y_column, 
    width_column, height_column, 
    x_scale_factor=1,
    y_scale_factor=1
    ): # for bounding boxes need to know if measurements are in pixels or mm
    bbox_xs = dataframe[centre_x_column]
    bbox_xs = bbox_xs.multiply(x_scale_factor)
    xs_array = bbox_xs.to_numpy(dtype=np.float16)

    bbox_ys = dataframe[centre_y_column]
    bbox_ys = bbox_ys.multiply(y_scale_factor)
    ys_array = bbox_ys.to_numpy(dtype=np.float16)


    bbox_widths = dataframe[width_column]
    bbox_widths = bbox_widths.multiply(x_scale_factor)
    widths_array = bbox_widths.to_numpy(dtype=np.float16)

    bbox_heights = dataframe[height_column]
    bbox_heights = bbox_heights.multiply(y_scale_factor)
    heights_array = bbox_heights.to_numpy(dtype=np.float16)

    array_tuple = (xs_array, ys_array, widths_array, heights_array)

    return array_tuple

# To read datasets where the class name is in the directory structure.
# i.e. covid/im001 or no-covid/im001
# pulls the class names from the path and reads in the images
# as a numpy array
def read_classes_in_directory_name(directory, image_file_wildcard, output_shape, class_level=1):
    path_to_search = directory + "/**/" + image_file_wildcard
    files = glob.glob(path_to_search, recursive=True)

    number_of_files = len(files)
    array_shape = (number_of_files,) + output_shape #concatonate the tuples
    array = np.zeros(array_shape, dtype=np.int16)
    classes = np.empty(number_of_files, dtype=object)

    for index, name in enumerate(files):
        parts = Path(name).parts
        class_name = parts[class_level]

        image = read.load_image(name)
        result = cv2.resize(image, output_shape)

        classes[index] = class_name
        array[index] = result
        
    return classes, array