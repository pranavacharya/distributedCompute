import json
import pytesseract
import numpy as np
import cv2 # OpenCV
import sys
input = sys.argv[1]

print(sys.argv)
def pytesseract_ocr(input_img):
    img=cv2.imread(input_img)
    rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    # cv2.imshow(window_name,rgb)
    #cv2.waitKey(0)
    text = pytesseract.image_to_string(rgb)
    return text
op=pytesseract_ocr(input)
print(op)