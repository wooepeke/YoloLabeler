
# YoloLabeler

This repository can contains the tools to label images in the yolo format.


## Authors

- [@Xavier Reparon](https://github.com/wooepeke)


## Features

- Create dataset with multiple boundingboxes in an image.
- Split data into training, test and validation set.
- Refactor boundingbox coordinates to the yolo format


## File Structure

The file structure for your project should look like this. Make sure to change your dataset files in the code.

```bash
./src
├── ...                       
├── Datasets                    # Compiled files (alternatively `dist`)
│   ├── SetNameOne              # Name of your dataset 
│   │   ├── annotated_images    # Annotated Images of your dataset 
│   │   ├── images              # Images of your dataset 
│   │   └── labels              # Labels of your dataset 
│   ├── SetNameTwo              # Name of your dataset 
│   │   ├── annotated_images    # Annotated Images of your dataset 
│   │   ├── images              # Images of your dataset 
│   │   └── labels              # Labels of your dataset 
│   └── SetNameThree            # Name of your dataset 
│   │   ├── annotated_images    # Annotated Images of your dataset 
│   │   ├── images              # Images of your dataset 
│   │   └── labels              # Labels of your dataset 
├── ...
└── README.md
```


## Deployment

To deploy this project run the following command.

```bash
../YoloLabeler/src> python3 Gui.py
```


## Instructions

Follow the instructions of the GUI
## TODO

- ~Create a better way to add and remove images to the dataset~
- ~Create a better way to handle wrongfully added data to the dataset~
- ~Create a better way to label parts of an image instead of having one possible label per image~
- ~Create a better way to name labels in images~
- Add yolo support and test on Linux Ubuntu 22.04/24.04
- ~Add nice GUI for using the program~
## License

[MIT](https://choosealicense.com/licenses/mit/)

