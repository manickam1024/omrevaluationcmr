import cv2
import pytesseract

# Optional: specify path to tesseract executable
# pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

def auto_rotate_image(image_path, output_path):
    # Load image
    image = cv2.imread(image_path)

    # Convert to gray
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # OCR to detect orientation
    osd = pytesseract.image_to_osd(gray)
    print("OSD Result:", osd)

    # Extract rotation angle from OSD result
    angle = 0
    for line in osd.split('\n'):
        if 'Rotate:' in line:
            angle = int(line.split(':')[1].strip())
            break

    # Correct rotation
    if angle != 0:
        print(f"Rotating image by {angle} degrees to correct orientation.")
        if angle == 90:
            rotated = cv2.rotate(image, cv2.ROTATE_90_COUNTERCLOCKWISE)
        elif angle == 180:
            rotated = cv2.rotate(image, cv2.ROTATE_180)
        elif angle == 270:
            rotated = cv2.rotate(image, cv2.ROTATE_90_CLOCKWISE)
    else:
        print("Image is already correctly oriented.")
        rotated = image

    # Save the rotated image
    cv2.imwrite(output_path, rotated)
    print(f"Saved corrected image to {output_path}")

# Example usage
auto_rotate_image("scanned_omr.jpg", "rotated_output.jpg")
