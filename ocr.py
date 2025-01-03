import os
from pdf2image import convert_from_path
from PIL import Image
import pytesseract
from multiprocessing import Pool

PDF_PATH = "input/math.pdf"
OUTPUT_DIR = "output"
os.makedirs(OUTPUT_DIR, exist_ok=True)

def preprocess_image(image):
    """
    Preprocess the image for better OCR results.
    """
    # Resize the image to reduce size
    img = image.resize((image.width // 2, image.height // 2))

    # Convert to grayscale
    img = img.convert("L")

    # Binarize the image
    img = img.point(lambda p: p > 128 and 255)

    return img

def process_page_with_tesseract(page_data):
    """
    Process a single PDF page using Tesseract OCR.
    """
    page_number, page_image = page_data
    try:
        print(f"Processing page {page_number}...")

        # Preprocess the image
        img = preprocess_image(page_image)

        # Save the processed image
        page_image_path = os.path.join(OUTPUT_DIR, f"page_{page_number}.jpg")
        img.save(page_image_path)
        print(f"Processed image saved for page {page_number}: {page_image_path}")

        # Perform OCR with optimized settings
        text = pytesseract.image_to_string(img, lang="eng", config="--oem 1 --psm 6")
        print(f"OCR completed for page {page_number}: {text[:50]}...")

        # Save the OCR results
        ocr_output_path = os.path.join(OUTPUT_DIR, f"page_{page_number}_ocr.txt")
        with open(ocr_output_path, "w") as f:
            f.write(text)

        return f"Page {page_number} processed successfully."

    except Exception as e:
        print(f"Error processing page {page_number}: {e}")
        return f"Error on page {page_number}"

def process_pdf(pdf_path, output_dir, dpi=150, num_processes=4):
    """
    Process a PDF file using multiprocessing and Tesseract OCR.
    """
    print(f"Processing PDF: {pdf_path}")

    if not os.path.exists(pdf_path):
        print(f"Error: PDF file not found: {pdf_path}")
        return

    try:
        pages = convert_from_path(pdf_path, dpi=dpi)
        page_data = [(page_num + 1, page) for page_num, page in enumerate(pages)]

        # Use multiprocessing for parallel processing
        with Pool(processes=num_processes) as pool:
            results = pool.map(process_page_with_tesseract, page_data)

        for result in results:
            print(result)

    except Exception as e:
        print(f"Error processing PDF: {e}")

if __name__ == "__main__":
    process_pdf(PDF_PATH, OUTPUT_DIR, dpi=500, num_processes=4)
