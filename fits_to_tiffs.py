import os
import json
from astropy.io import fits
from PIL import Image
import numpy as np
from tqdm import tqdm  

def tiffer(source_folder):
    """ Converts all FITS files in a folder to TIFF format. """
    destination_folder = os.path.join(source_folder, "converted")
    os.makedirs(destination_folder, exist_ok=True)  # Create "converted" folder if missing

    # Read shotsInfo.json if available
    json_path = os.path.join(source_folder, "shotsInfo.json")
    if os.path.exists(json_path):
        with open(json_path, 'r') as json_file:
            shots_info = json.load(json_file)
            print("shotsInfo.json content:")
            print(json.dumps(shots_info, indent=4))  # Pretty-print JSON

    # Get FITS files (ignore "stacked" files)
    fits_files = [file_name for file_name in os.listdir(source_folder) if file_name.endswith(".fits") and not file_name.lower().startswith("stacked")]

    # Process files with a progress bar
    for file_name in tqdm(fits_files, desc=f"Processing {os.path.basename(source_folder)}", unit="file"):
        fits_path = os.path.join(source_folder, file_name)
        tiff_path = os.path.join(destination_folder, file_name.replace(".fits", ".tiff"))

        # Load FITS file
        with fits.open(fits_path) as hdul:
            data = hdul[0].data  # Get image data

        data = np.squeeze(data)  # Remove extra dimensions

        # Ensure 2D image
        if len(data.shape) != 2:
            print(f"Skipping {file_name} - Unexpected shape: {data.shape}")
            continue

        # Normalize to 8-bit
        data = (data - np.min(data)) / (np.max(data) - np.min(data))  # Normalize to 0-1
        data = (data * 255).astype(np.uint8)  # Scale to 8-bit

        # Save as TIFF
        Image.fromarray(data).save(tiff_path)

    print(f"✅ Conversion completed for: {source_folder}")

if __name__ == "__main__":
    source_folders = []

    # Loop to take multiple folder inputs
    while True:
        folder = input("Enter a folder path (or press Enter to start processing): ").strip()
        if not folder:
            break  # Exit loop if input is empty
        if os.path.exists(folder):
            source_folders.append(folder)
        else:
            print(f"⚠️ Folder not found: {folder}")

    # Process collected folders
    if source_folders:
        for folder in source_folders:
            tiffer(folder)
    else:
        print("❌ No valid folders provided. Exiting.")
