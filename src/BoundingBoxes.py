import cv2
import json
import os
 
# Configuration
OUTPUT_FOLDER = 'Datasets/Stag/labels'  # Folder where the JSON is saved --> Rename this 
CLASS_LABEL = 0  # Default class label for annotations
json_filepath = os.path.join(OUTPUT_FOLDER, 'labeled_regions.json')  # Update this with the appropriate JSON filename

# Function to load annotations from JSON file
def load_annotations(json_filepath):
    with open(json_filepath, 'r') as f:
        return json.load(f)

# Function to draw bounding boxes on an image
def draw_bounding_boxes(image, annotations, image_file):
    if image_file in annotations:
        for annotation in annotations[image_file]:
            class_label, x_center, y_center, width, height = annotation
            # Convert from normalized to absolute coordinates (original image size)
            img_height, img_width = image.shape[:2]
            x1 = int((x_center - width / 2) * img_width)
            y1 = int((y_center - height / 2) * img_height)
            x2 = int((x_center + width / 2) * img_width)
            y2 = int((y_center + height / 2) * img_height)

            # Draw the bounding box
            cv2.rectangle(image, (x1, y1), (x2, y2), (0, 255, 0), 2)

            # Optionally, add a label for the class
            cv2.putText(image, f"Class: {class_label}", (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)
    return image

# Load annotations from JSON file
annotations = load_annotations(json_filepath)

# Get the list of image files from the annotations
image_files = list(annotations.keys())

# Initialize index for current image
current_index = 0

# Function to display the image with bounding boxes
def display_image_with_boxes(image_file):
    image_path = os.path.join('Datasets/Stag/images', image_file)

    # Load the image
    if not os.path.exists(image_path):
        print(f"Image {image_file} not found at {image_path}")
        return

    image = cv2.imread(image_path)
    img_height, img_width = image.shape[:2]

    # Resize the image for displaying if necessary (maintains aspect ratio)
    screen_width = 1920  # Default screen width
    screen_height = 1080  # Default screen height
    aspect_ratio = img_width / img_height

    if img_width > screen_width or img_height > screen_height:
        if aspect_ratio > 1:  # Landscape orientation
            new_width = screen_width
            new_height = int(screen_width / aspect_ratio)
        else:  # Portrait orientation
            new_height = screen_height
            new_width = int(screen_height * aspect_ratio)
        image_display = cv2.resize(image, (new_width, new_height))
    else:
        image_display = image.copy()

    # Draw bounding boxes on the resized image
    image_with_boxes = draw_bounding_boxes(image_display.copy(), annotations, image_file)

    # Create a resizable window and show the image
    cv2.namedWindow('Image with Bounding Boxes', cv2.WINDOW_NORMAL)
    cv2.imshow('Image with Bounding Boxes', image_with_boxes)

# Main loop to cycle through images
while True:
    # Display the current image with bounding boxes
    display_image_with_boxes(image_files[current_index])

    print(f"Viewing {image_files[current_index]} - Press 'a' for previous image, 'd' for next image, or 'q' to quit.")

    # Wait for user input
    key = cv2.waitKey(0) & 0xFF

    if key == ord('d'):  # Next image
        current_index = (current_index + 1) % len(image_files)  # Loop to the next image
    elif key == ord('a'):  # Previous image
        current_index = (current_index - 1) % len(image_files)  # Loop to the previous image
    elif key == ord('q'):  # Quit the program
        print("Exiting.")
        break

    # Close the previous window before continuing to the next image
    cv2.destroyAllWindows()

cv2.destroyAllWindows()
