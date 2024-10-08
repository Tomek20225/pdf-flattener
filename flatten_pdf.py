import platform
import sys
import os
import shutil
import tempfile
import fitz
from pdf2image import convert_from_path
from datetime import datetime
import subprocess

DPI = 200

def get_poppler_path():
    if platform.system() == "Windows":
        poppler_path = r'C:\Program Files\poppler-0.68.0\bin'  # Update with your Windows poppler path
        if not os.path.exists(poppler_path):
            print("Error: Poppler not found at the specified path. Please install Poppler or update the path.")
            sys.exit(1)
        return poppler_path
    elif platform.system() in ["Linux", "Darwin"]:  # Darwin is macOS
        if not shutil.which("pdftoppm"):
            print("Error: Poppler utilities not found. Please install Poppler (Linux: sudo apt-get install poppler-utils, macOS: brew install poppler).")
            sys.exit(1)
        return None
    else:
        print("Error: Unsupported operating system. This script supports Windows, macOS, and Linux.")
        sys.exit(1)

def extract_images_from_pdf(pdf_path, dpi=DPI):
    poppler_path = get_poppler_path()
    images = convert_from_path(pdf_path, dpi=dpi, poppler_path=poppler_path)
    return images

def create_pdf_from_images(images, output_path):
    doc = fitz.open()
    
    for image in images:
        with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as temp_img_file:
            image.save(temp_img_file, format='JPEG', quality=50)
            temp_img_file_path = temp_img_file.name
        
        img_pix = fitz.Pixmap(temp_img_file_path)
        page = doc.new_page(width=img_pix.width, height=img_pix.height)
        page.insert_image(page.rect, pixmap=img_pix)

        img_pix = None
        os.remove(temp_img_file_path)
    
    doc.save(output_path)
    doc.close()

def compress_pdf(input_pdf, output_pdf):
    doc = fitz.open(input_pdf)
    doc.save(output_pdf, 
             garbage=4,
             deflate=True,
             incremental=False,
             clean=True)
    doc.close()

def set_metadata(pdf_path, creation_date=None, modification_date=None):
    doc = fitz.open(pdf_path)

    def format_date(dt):
        return dt.strftime("D:%Y%m%d%H%M%S+00'00'")

    # Prepare the metadata dictionary
    new_metadata = {}

    if creation_date:
        try:
            creation_dt = datetime.strptime(creation_date, "%Y-%m-%d")
            creation_str = format_date(creation_dt)
            new_metadata['creationDate'] = creation_str
        except ValueError:
            print("Invalid creation date format. Use YYYY-MM-DD.")
            return

    if modification_date:
        try:
            modification_dt = datetime.strptime(modification_date, "%Y-%m-%d")
            modification_str = format_date(modification_dt)
            new_metadata['modDate'] = modification_str
        except ValueError:
            print("Invalid modification date format. Use YYYY-MM-DD.")
            return

    # Update metadata after compression
    doc.set_metadata(new_metadata)
    doc.save(pdf_path, incremental=True, encryption=fitz.PDF_ENCRYPT_KEEP)
    doc.close()

def flatten_pdf(pdf_path, output_path, creation_date=None, modification_date=None, dpi=DPI):
    temp_output_path = tempfile.NamedTemporaryFile(suffix=".pdf", delete=False).name
    images = extract_images_from_pdf(pdf_path, dpi)
    create_pdf_from_images(images, temp_output_path)

    compressed_output_path = tempfile.NamedTemporaryFile(suffix=".pdf", delete=False).name
    compress_pdf(temp_output_path, compressed_output_path)

    # Retrieve the original file's metadata dates
    doc = fitz.open(pdf_path)
    original_metadata = doc.metadata
    original_creation_date = original_metadata.get("creationDate", "")
    original_modification_date = original_metadata.get("modDate", "")
    doc.close()

    # Extract and format the original creation and modification datetime if they exist
    if original_creation_date:
        original_creation_dt = datetime.strptime(original_creation_date[2:16], "%Y%m%d%H%M%S")
    else:
        original_creation_dt = datetime.fromtimestamp(os.path.getctime(pdf_path))

    if original_modification_date:
        original_modification_dt = datetime.strptime(original_modification_date[2:16], "%Y%m%d%H%M%S")
    else:
        original_modification_dt = datetime.fromtimestamp(os.path.getmtime(pdf_path))

    # Use original hours and minutes if only the date part is provided
    if creation_date:
        creation_date = datetime.strptime(creation_date, "%Y-%m-%d")
        creation_dt = creation_date.replace(hour=original_creation_dt.hour, 
                                            minute=original_creation_dt.minute, 
                                            second=original_creation_dt.second)
    else:
        creation_dt = original_creation_dt

    if modification_date:
        modification_date = datetime.strptime(modification_date, "%Y-%m-%d")
        modification_dt = modification_date.replace(hour=original_modification_dt.hour, 
                                                    minute=original_modification_dt.minute, 
                                                    second=original_modification_dt.second)
    else:
        modification_dt = original_modification_dt

    # Ensure modification date is not earlier than the creation date
    if modification_dt < creation_dt:
        modification_dt = creation_dt

    # Set metadata after compression
    set_metadata(compressed_output_path, creation_dt.strftime("%Y-%m-%d"), modification_dt.strftime("%Y-%m-%d"))

    # Move final compressed and metadata-set file to the intended output location
    shutil.move(compressed_output_path, output_path)

    # Set file system times if creation/modification dates are provided
    set_file_times(output_path, creation_dt, modification_dt)

    # Clean up temporary files
    os.remove(temp_output_path)

def set_file_times(file_path, creation_dt, modification_dt):
    # Apply modification and access times
    mod_timestamp = modification_dt.timestamp()
    os.utime(file_path, (mod_timestamp, mod_timestamp))

    if platform.system() == "Darwin":  # macOS only
        try:
            # Set the creation date first
            creation_str = creation_dt.strftime("%Y%m%d%H%M")
            subprocess.run(["touch", "-t", creation_str, file_path], check=True)

            # Set the modification date separately using os.utime() to prevent touch from affecting it
            os.utime(file_path, (mod_timestamp, mod_timestamp))
        except subprocess.CalledProcessError as e:
            print(f"Error setting file creation date: {e}")

def parse_arguments():
    import argparse
    parser = argparse.ArgumentParser(description="Flatten a PDF and optionally set metadata.")

    parser.add_argument("input_pdf", help="Path to the input PDF file")
    parser.add_argument("--output", "-o", help="Output PDF file name", default=None)
    parser.add_argument("--dpi", "-d", type=int, help="DPI for image extraction (default: 200)", default=200)
    parser.add_argument("--creation-date", "-c", help="Creation date in YYYY-MM-DD format", default=None)
    parser.add_argument("--modification-date", "-m", help="Modification date in YYYY-MM-DD format", default=None)

    return parser.parse_args()

def main():
    args = parse_arguments()

    input_pdf = args.input_pdf
    output_pdf = args.output if args.output else f"flat-{os.path.basename(input_pdf)}"
    creation_date = args.creation_date
    modification_date = args.modification_date
    dpi = args.dpi

    flatten_pdf(input_pdf, output_pdf, creation_date, modification_date, dpi)

    print(f"File {output_pdf} saved successfully.")

if __name__ == "__main__":
    main()
