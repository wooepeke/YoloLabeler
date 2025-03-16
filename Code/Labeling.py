import cv2
import os
import json

# Configuration
IMAGE_FOLDER = 'Datasets/Stag/images'
OUTPUT_FOLDER = 'Datasets/Stag/labels'  # Folder to store annotation files
CLASS_LABEL = 0  # Default class label for annotations

# Ensure output folder exists
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

# Set the JSON filename without timestamp
json_filename = "labeled_regions.json"
json_filepath = os.path.join(OUTPUT_FOLDER, json_filename)

# Initialize variables
regions = []
current_region = []
drawing = False
annotations = {}  # To store all YOLOv5 annotations

def draw_region(event, x, y, flags, param):
    global current_region, drawing, regions

    if event == cv2.EVENT_LBUTTONDOWN:
        # Start drawing a region
        drawing = True
        current_region = [(x, y)]

    elif event == cv2.EVENT_MOUSEMOVE:
        if drawing:
            # Update the current region's shape
            img_copy = image_display.copy()
            # Draw all previous rectangles
            for region in regions:
                cv2.rectangle(img_copy, tuple(region['start_point']), tuple(region['end_point']), (0, 255, 0), 2)
            # Draw the currently being drawn rectangle
            cv2.rectangle(img_copy, current_region[0], (x, y), (0, 255, 0), 2)
            cv2.imshow('Labeling Tool', img_copy)

    elif event == cv2.EVENT_LBUTTONUP:
        # Finalize the region
        drawing = False
        current_region.append((x, y))
        regions.append({
            'start_point': current_region[0],
            'end_point': current_region[1]
        })
        print(f"Region added: {current_region}")
        current_region = []

# List all images in the folder
image_files = [f for f in os.listdir(IMAGE_FOLDER) if f.lower().endswith(('.png', '.jpg', '.jpeg'))]

for image_file in image_files:
    IMAGE_PATH = os.path.join(IMAGE_FOLDER, image_file)
    regions = []  # Reset regions for the new image

    print(f"Processing: {IMAGE_PATH}")

    # Load the image
    if not os.path.exists(IMAGE_PATH):
        print(f"Error: Image not found at {IMAGE_PATH}")
        continue

    image = cv2.imread(IMAGE_PATH)
    img_height, img_width = image.shape[:2]

    # Resize the image to fit the screen if needed
    screen_width = 2559  # Default screen width
    screen_height = 1439  # Default screen height
    aspect_ratio = image.shape[1] / image.shape[0]

    if image.shape[1] > screen_width or image.shape[0] > screen_height:
        if aspect_ratio > 1:  # Landscape orientation
            new_width = screen_width
            new_height = int(screen_width / aspect_ratio)
        else:  # Portrait orientation
            new_height = screen_height
            new_width = int(screen_height * aspect_ratio)
        image_display = cv2.resize(image, (new_width, new_height))
    else:
        image_display = image.copy()

    # Create a full-screen window
    cv2.namedWindow('Labeling Tool', cv2.WINDOW_NORMAL)
    cv2.setWindowProperty('Labeling Tool', cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
    cv2.setMouseCallback('Labeling Tool', draw_region)

    print("Instructions:")
    print("- Draw regions by clicking and dragging.")
    print("- Press 's' to save and move to the next image.")
    print("- Press 'Ctrl+Z' to undo the last region.")
    print("- Press 'n' to skip this image.")
    print("- Press 'q' to stop the tool completely.")

    stop_tool = False  # Flag to stop the tool entirely

    while True:
        # Redraw all rectangles every time the window refreshes
        img_copy = image_display.copy()
        for region in regions:
            cv2.rectangle(img_copy, tuple(region['start_point']), tuple(region['end_point']), (0, 255, 0), 2)
        cv2.imshow('Labeling Tool', img_copy)

        key = cv2.waitKey(1)

        # Check for undo (Ctrl+Z)
        if key == 26:  # ASCII code for Ctrl+Z
            if regions:
                removed_region = regions.pop()
                print(f"Removed last region: {removed_region}")
            else:
                print("No regions to undo!")

        elif key == ord('s'):  # Save and move to the next image
            annotations[image_file] = []
            txt_filename = f"{os.path.splitext(image_file)[0]}.txt"
            txt_filepath = os.path.join(OUTPUT_FOLDER, txt_filename)

            with open(txt_filepath, 'w') as txt_file:
                for region in regions:
                    # Normalize coordinates
                    x1, y1 = region['start_point']
                    x2, y2 = region['end_point']
                    x_center = ((x1 + x2) / 2) / img_width
                    y_center = ((y1 + y2) / 2) / img_height
                    width = abs(x2 - x1) / img_width
                    height = abs(y2 - y1) / img_height
                    # Include CLASS_LABEL in the annotation
                    annotations[image_file].append([CLASS_LABEL, x_center, y_center, width, height])
                    # Save to the image-specific text file
                    txt_file.write(f"{CLASS_LABEL} {x_center} {y_center} {width} {height}\n")
            print(f"Regions saved for {image_file}")
            break

        elif key == ord('n'):  # Skip this image
            print("Skipping this image.")
            break

        elif key == ord('q'):  # Stop the tool completely
            print("Stopping the tool.")
            stop_tool = True
            break

    cv2.destroyAllWindows()

    if stop_tool:
        break  # Exit the outer loop

# Save all annotations to a single JSON file
with open(json_filepath, 'w') as json_file:
    json.dump(annotations, json_file, indent=4)

print(f"All annotations saved to {json_filepath} and individual .txt files.")
