import cv2
import cvzone
import math
import numpy as np
from ultralytics import YOLO
from PIL import ImageFont, ImageDraw, Image
import os

# Load the Arabic font (Make sure the file is in the correct directory)
font_path = os.path.abspath("NotoNaskhArabic-VariableFont_wght.ttf")  # Change path if needed
font = ImageFont.truetype(font_path, 36)  # Adjust font size

vid3 = "../videos/ff_car.mp4"
cap = cv2.VideoCapture(vid3)

# Load YOLO model for plate detection
model = YOLO('runs/detect/train6/weights/best.pt')
classnames = ['نمبر پلیت']  # Dari class label

def draw_text_with_pil(image, text, position):
    """Draw Dari text using PIL for correct rendering."""
    image_pil = Image.fromarray(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
    draw = ImageDraw.Draw(image_pil)
    draw.text(position, text, font=font, fill=(255, 255, 255))  # White text
    return cv2.cvtColor(np.array(image_pil), cv2.COLOR_RGB2BGR)

while True:
    ret, frame = cap.read()
    if not ret:
        break  # Break the loop if the video ends

    frame = cv2.resize(frame, (1080, 720))  # Resize frame for better performance
    results = model(frame)  # Run YOLO model

    for info in results:
        for box in info.boxes:
            x1, y1, x2, y2 = map(int, box.xyxy[0])  # Bounding box coordinates
            confidence = box.conf[0]  # Confidence score
            class_detect = int(box.cls[0])  # Class index
            class_detect = classnames[class_detect]  # Map index to class name

            # Draw bounding box
            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)

            # Display Dari text properly
            frame = draw_text_with_pil(frame, f'{class_detect}', (x1 + 8, y1 - 40))

    cv2.imshow('frame', frame)

    # Exit loop when 't' key is pressed
    if cv2.waitKey(1) & 0xFF == ord('t'):
        break

cap.release()
cv2.destroyAllWindows()
