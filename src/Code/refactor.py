import json

# Path to the annotations JSON file
ANNOTATIONS_PATH = 'Datasets/Stag/labels/labeled_regions.json'

# Read the data from the JSON file
with open(ANNOTATIONS_PATH, 'r') as f:
    data = json.load(f)

# Loop through the data and generate a separate file for each screenshot
for key, regions in data.items():
    # Extract screenshot number from the key (e.g., Screenshot_1.png -> 1)
    screenshot_num = key.split('_')[1].split('.')[0]
    
    # Prepare the content for the current file
    output_lines = []
    for region in regions:
        # Convert the region to a space-separated string
        output_lines.append(' '.join(map(str, region)))  # Join the numbers with spaces
    
    # Prepare the content for the labeled_region<i>.txt file
    output_text = "\n".join(output_lines)

    # File path to save the output for each screenshot
    output_file_path = f'Datasets/Stag/labels/Screenshot_{screenshot_num}.txt'

    # Write the output to the corresponding file
    with open(output_file_path, 'w') as f:
        f.write(output_text)

    print(f"File saved to {output_file_path}")
