import sys, json, time
import torch
import random
import fitz
import os
import re
import statistics, csv
from tqdm import tqdm
from PIL import Image
from pathlib import Path
from typing import Iterable, List, Union
Image.MAX_IMAGE_PIXELS = 1_000_000_000

def write_csv(output_csv, merged_data, fieldnames):
    with open(output_csv, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, delimiter='|', extrasaction='ignore')
        writer.writeheader()
        for record in merged_data:
            # Replace actual newlines with literal "\n" in all string fields
            for k, v in record.items():
                if isinstance(v, str):
                    # Escape \n and \r so they appear as literal text in the CSV
                    v = v.replace('\n', '\\n').replace('\r', '\\r')
                    record[k] = v
            writer.writerow(record)

class jsonl:
    def read(file_path):
        data = []
        with open(file_path, 'r') as file:
            for line in file:
                data.append(json.loads(line))
        return data
    
    def write(out_path, data):
        out_dir = Path(out_path).parent
        out_dir.mkdir(parents=True, exist_ok=True)
        with open(out_path, "w", encoding="utf-8") as f:
            for entry in data:
                f.write(json.dumps(entry) + "\n")

    def read_text(text, delimiter="\n"):
        data = []
        # Split the text by the given delimiter into individual lines
        lines = text.split(delimiter)
        for line in lines:
            line = line.strip()  # Remove leading/trailing whitespace
            if not line:
                continue  # Skip empty lines
            # Parse the JSON content in each line
            try:
                json_dict = json.loads(str(line))
                data.append(json_dict)
            except json.JSONDecodeError:
                # Line isn’t valid JSON—skip it (or log if you prefer)
                print(f"WARNING: Could not parse \"{line}\"")

        return data
    
    def parse_filenames(filenames: Union[str, Iterable[str]], image_dir) -> List[Path]:
        # ---- normalise to a list of strings ----
        if isinstance(filenames, (list, tuple, set)):
            file_list = filenames
        else:                               # treat as str
            file_list = str(filenames).split(",")

        # ---- build Path objects, trimming whitespace ----
        image_paths = [
            image_dir / fname.strip()
            for fname in file_list
            if fname.strip()                 # skip empty pieces
        ]

        return image_paths
    
    def jsonl_to_csv(path, fieldnames):
        jsonl_file = jsonl.read(path)

        output_csv = Path(path).stem + '.csv'

        write_csv(output_csv, jsonl_file, fieldnames)
        
        print(f"Finished merging. {len(jsonl_file)} records written to {output_csv}")

    def csv_to_jsonl(csv_path):
        # Read CSV rows into a list of dictionaries
        with open(csv_path, 'r', encoding='utf-8-sig') as f:
            reader = csv.DictReader(f)
            rows = [row for row in reader]

        # Determine the output file name (e.g., myfile.csv -> myfile.jsonl)
        output_jsonl = Path(csv_path).parent / (Path(csv_path).stem + '.jsonl')

        # Write each row as a JSON object on its own line
        with open(output_jsonl, 'w', encoding='utf-8') as out:
            for row in rows:
                out.write(json.dumps(row, ensure_ascii=False) + '\n')

        print(f"Finished converting CSV to JSONL. {len(rows)} records written to {output_jsonl}")

class padding:
    def right(batch_list: list[list], pad=0):
        max_len = max(len(sublist) for sublist in batch_list)

        return [sublist + [pad] * (max_len - len(sublist))
                for sublist in batch_list]

def test_train_split(data, split = .2, determ=False):
    data_copy = data[:]
    assert 0 < split and split < 1, "split should be percentage between 0 and 1"
    
    if not determ:    
        random.shuffle(data_copy)
        
    return (data_copy[:int((1-split)*len(data_copy))], data_copy[int((1-split)*len(data_copy)):])

class ImageConverter:
    def convert_all_pdfs(folder):
        for file_name in os.listdir(folder):
            file_path = os.path.join(folder, file_name)
            if file_name.lower().endswith('.pdf'):
                print(f"Processing: {file_name}")
                pdf_document = fitz.open(file_path)
                
                # Render all pages into images
                images = []
                for page_number in range(len(pdf_document)):
                    page = pdf_document.load_page(page_number)
                    pix = page.get_pixmap()
                    img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
                    images.append(img)

                pdf_document.close()

                # Concatenate images vertically
                if len(images) > 1:
                    # Calculate total height and max width
                    total_height = sum(img.height for img in images)
                    max_width = max(img.width for img in images)

                    # Create a blank image
                    combined_image = Image.new("RGB", (max_width, total_height))

                    # Paste images one below the other
                    y_offset = 0
                    for img in images:
                        combined_image.paste(img, (0, y_offset))
                        y_offset += img.height

                    # Save the concatenated image
                    output_file = Path(folder) / f"{file_name[:-4]}.png"
                    combined_image.save(output_file)
                    print(f"Saved: {output_file}")
                elif len(images) == 1:
                    # If only one page, just save it as is
                    output_file = Path(folder) / f"{file_name[:-4]}.png"
                    images[0].save(output_file)
                    print(f"Saved: {output_file}")

    def convert_pdf(filepath, output_path=None, dpi=150, overwrite=False):
        zoom_factor = dpi / 72  # Calculate zoom factor for the desired DPI

        filename = os.path.splitext(os.path.basename(filepath))[0]

        if output_path is None:
            output_path = os.path.dirname(filepath)

        # Open the PDF file
        doc = fitz.open(filepath)

        # Iterate through each page
        for i in range(len(doc)):
            page = doc.load_page(i)  # number of page
            # Create a pixmap with custom zoom
            mat = fitz.Matrix(zoom_factor, zoom_factor)  # Apply the zoom factor
            pix = page.get_pixmap(matrix=mat)  # Use the matrix to render the page
            save_path = f"{output_path}/{filename}"
            if i > 0:
                save_path+= f"_{i+1}.png"
            else:
                save_path+= ".png"
            
            if os.path.exists(save_path) and overwrite is False:
                print(f"Unable to save. File: {save_path} already exists!\nSet overwrite=True to suppress warning")
            else:
                pix.save(save_path)
                print("Conversion completed at {} DPI.".format(dpi))

    def convert_jp2(filepath, output_path=None, overwrite=False):
        filename = os.path.splitext(os.path.basename(filepath))[0]

        if output_path is None:
            output_path = os.path.dirname(filepath)

        save_path = f"{output_path}/{filename}.jpg"

        with Image.open(filepath) as image:
            if image.mode in ('RGBA', 'LA'):
                image = image.convert('RGB')

            if os.path.exists(save_path) and overwrite is False:
                print(f"Unable to save. File: {save_path} already exists!\nSet overwrite=True to suppress warning")
            else:
                image.save(save_path, 'JPEG')

    def convert_tif(filepath, output_path=None, dpi=150, overwrite=False):
        filename = os.path.splitext(os.path.basename(filepath))[0]

        if output_path is None:
            output_path = os.path.dirname(filepath)

        save_path = f"{output_path}/{filename}.jpg"

        with Image.open(filepath) as image:
            # Convert from "P" mode (indexed color) or "RGBA"/"LA" to "RGB"
            if image.mode != 'RGB':
                image = image.convert('RGB')

            # If file already exists and we don't want to overwrite, skip
            if os.path.exists(save_path) and not overwrite:
                print(f"Unable to save. File: {save_path} already exists!\n"
                    "Set overwrite=True to suppress warning")
            else:
                # Optionally embed DPI in the output if desired:
                # image.save(save_path, "JPEG", dpi=(dpi, dpi))
                image.save(save_path, "JPEG")

    def resize_image(filepath, target_width, target_height, output_path=None):
        valid_exts = ['.png', '.jpg', '.jpeg', '.JPG', '.webp']
        ext = os.path.splitext(filepath)[1].lower()
        if ext not in valid_exts:
            raise ValueError("Only PNG, JPG, and WEBP images are supported.")

        if output_path is None:
            output_path = filepath
        else:
            _, tail = os.path.split(filepath)
            output_path = os.path.join(output_path, tail)
        
        # Open the image
        with Image.open(filepath) as img:
            orig_width, orig_height = img.size
        
            # Only resize if image dimensions exceed the target dimensions
            if orig_width <= target_width and orig_height <= target_height:
                if output_path:
                    img.save(output_path)
                    return
                return  # Return original file path
            
            # Compute scale factor to retain aspect ratio
            scale_factor = min(target_width / orig_width, target_height / orig_height)
            new_width = int(orig_width * scale_factor)
            new_height = int(orig_height * scale_factor)
            
            # Resize the image using a high-quality filter
            resized_img = img.resize((new_width, new_height), Image.LANCZOS)
            
            # Save the image using the correct format
            if ext in ['.jpg', '.jpeg']:
                resized_img.save(output_path, format="JPEG", quality=95)
            elif ext == '.png':
                resized_img.save(output_path, format="PNG")
            elif ext == '.webp':
                resized_img.save(output_path, format="WEBP", quality=95)
        
        return output_path
    
    def image_metrics(dir):
        widths = []
        heights = []
        aspects = []

        # Aspect Ratio is width:height
        for filename in tqdm(os.listdir(dir), desc="Computing Image Metrics"):
            filepath = os.path.join(dir, filename)
            with Image.open(filepath) as img:
                width, height = img.size
                widths.append(width)
                heights.append(height)
                aspects.append(width/height)

        print("Width:")
        print(f'\tMean: {statistics.mean(widths)}')
        print(f'\tMedian: {statistics.median(widths)}')
        print(f'\tStd Dev: {statistics.stdev(widths)}')
        print(f'\tMax: {max(widths)}')
        print(f'\tMin: {min(widths)}')
        print()
        print("Height:")
        print(f'\tMean: {statistics.mean(heights)}')
        print(f'\tMedian: {statistics.median(heights)}')
        print(f'\tStd Dev: {statistics.stdev(heights)}')
        print(f'\tMax: {max(heights)}')
        print(f'\tMin: {min(heights)}')
        print()
        print("Aspect Ratio:")
        print(f'\tMean: {statistics.mean(aspects)}')
        print(f'\tMedian: {statistics.median(aspects)}')
        print(f'\tStd Dev: {statistics.stdev(aspects)}')
        print(f'\tMax: {max(aspects)}')
        print(f'\tMin: {min(aspects)}')
        print()

class APIKeyFile:
    def parse(filename):
        try:
            with open(filename, 'r') as file:
                for line in file:
                    # Remove content after any inline comment
                    line = line.split('#', 1)[0]
                    # Strip whitespace from the beginning and end of the line
                    stripped_line = line.strip()
                    # Check if the line is not empty
                    if stripped_line:
                        return stripped_line
        except FileNotFoundError:
            print(f"The {filename} was not found.")
        
        return None  # Return None if no key is found or an error occurs

def split_alnum_and_lower(text):
    """
    Removes non-alphanumeric and non-space characters then lowercases then splits into words.
    """
    return ''.join(c for c in text if c.isalnum() or c.isspace()).lower().split()

def word_count(text: str) -> int:
    # counts tokens like "don't", "co-op", "naïve", "O'Reilly"
    tokens = re.findall(r"[^\W_]+(?:['’-][^\W_]+)*", text, flags=re.UNICODE)
    return len(tokens)
