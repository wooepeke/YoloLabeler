import torch
from IPython.display import Image  # for displaying images
import os 
import random
import shutil
from sklearn.model_selection import train_test_split
import xml.etree.ElementTree as ET
from xml.dom import minidom
from tqdm import tqdm
from PIL import Image, ImageDraw
import numpy as np
import matplotlib.pyplot as plt

random.seed(42)

# Read images and annotations
IMAGE_PATH = 'Datasets/Stag/images'
ANNOTATIONS_PATH = 'Datasets/Stag/labels'

images = [os.path.join(IMAGE_PATH, x) for x in os.listdir(IMAGE_PATH) if x[-3:] == "png"]
annotations = [os.path.join(ANNOTATIONS_PATH, x) for x in os.listdir(ANNOTATIONS_PATH) if x[-3:] == "txt"]

images.sort()
annotations.sort()

# Split the dataset into train-valid-test splits 
train_images, val_images, train_annotations, val_annotations = train_test_split(images, annotations, test_size = 0.2, random_state = 1)
val_images, test_images, val_annotations, test_annotations = train_test_split(val_images, val_annotations, test_size = 0.5, random_state = 1)

#Utility function to move images 
def move_files_to_folder(list_of_files, destination_folder):
    for f in list_of_files:
        try:
            shutil.move(f, destination_folder)
        except:
            print(f)
            assert False

# Move the splits into their folders
move_files_to_folder(train_images, 'Datasets/Stag/images/train')
move_files_to_folder(val_images, 'Datasets/Stag/images/val/')
move_files_to_folder(test_images, 'Datasets/Stag/images/test/')
move_files_to_folder(train_annotations, 'Datasets/Stag/labels/train/')
move_files_to_folder(val_annotations, 'Datasets/Stag/labels/val/')
move_files_to_folder(test_annotations, 'Datasets/Stag/labels/test/')