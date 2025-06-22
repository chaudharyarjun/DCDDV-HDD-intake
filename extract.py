import cv2
import pytesseract
import re
import numpy as np

def process_image(image_bytes):
    npimg = np.frombuffer(image_bytes, np.uint8)
    img = cv2.imdecode(npimg, cv2.IMREAD_COLOR)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    sharpened = cv2.addWeighted(gray, 1.5, cv2.GaussianBlur(gray, (0,0), 3), -0.5, 0)
    text = pytesseract.image_to_string(sharpened)

    return {
        "raw_text": text,
        "model": re.findall(r'ST\d{4,}', text),
        "serial": re.findall(r'[A-Z0-9]{8,12}', text),
        "capacity": re.findall(r'\d+TB', text),
        "brand": "Seagate" if "Seagate" in text else None
    }
