# import cv2
# import numpy as np
# from ultralytics import YOLO
# import easyocr
# import sqlite3
# from datetime import datetime
# import cvzone

# from scripts.database_handler import insert_ocr_text
# # Load video
# video_path = 0 # Use webcam or video file
# cap = cv2.VideoCapture(video_path)

# # Load YOLO model
# model = YOLO('runs/detect/train6/weights/best.pt')

# # Initialize EasyOCR reader (using CPU, supporting only English)
# reader = easyocr.Reader(['en'], gpu=False)  # Only English

# def preprocess_plate(plate_img):
#     # Convert to grayscale
#     gray = cv2.cvtColor(plate_img, cv2.COLOR_BGR2GRAY)

#     # Apply GaussianBlur to reduce noise before thresholding
#     blurred = cv2.GaussianBlur(gray, (5, 5), 0)

#     # Apply binary thresholding to emphasize the text
#     _, thresholded = cv2.threshold(blurred, 150, 255, cv2.THRESH_BINARY)

 

#     return thresholded


# # Create a dictionary to store detected text based on bounding box coordinates
# detected_text = {}



# while True:
#     ret, frame = cap.read()
#     if not ret:
#         break

#     frame = cv2.resize(frame, (1080, 720))
#     results = model(frame)

#     for info in results:
#         parameters = info.boxes
#         for box in parameters:
#             x1, y1, x2, y2 = map(int, box.xyxy[0])
#             confidence = float(box.conf[0]) * 100  # Convert to percentage
            
#             # Draw bounding box
#             cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 244, 0), 2)
           
#             if confidence > 80:  # Only process if confidence is greater than 60%
#                 # Check if we have already detected text for this region
#                 box_key = (x1, y1, x2, y2)
                
#                 # Crop detected plate region
#                 plate_image = frame[y1:y2, x1:x2]
                
#                 # Crop the bottom half of the detected plate (y2 to the middle)
#                 # height = plate_image.shape[0]
#                 # bottom_half = plate_image[height//2:, :]  # Crop the bottom half
#                 height, width = plate_image.shape[:2]  # Get image height and width

#                 # Crop the bottom half
#                 bottom_half = plate_image[height//2:, :]

#                 # Crop the right 70% of the bottom half (removes 30% from the left)
#                 cropped_plate = bottom_half[:, int(width * 0.9):]

                
#                 # Preprocess the bottom half of the plate for better OCR (grayscale only)
#                 plate_image = preprocess_plate(bottom_half)
                
#                 # OCR to read text from the plate
#                 result = reader.readtext(plate_image)
#                 if result:
#                     # Extract the OCR text
#                     ocr_text = ' '.join([res[1] for res in result])
                    
#                     # Check OCR confidence and only display text if confidence > 90%
#                     if result[0][2] > 0.50:  # result[0][2] is the confidence score
#                         detected_text[box_key] = ocr_text
                        
#                         # Insert detected OCR text into the SQLite database
#                         insert_ocr_text(ocr_text)
#                     else:
#                         detected_text[box_key] = ""
                        
#                 elif box_key not in detected_text:
#                     # If no text is detected, retain the old value for that box
#                     detected_text[box_key] = ""

#                 # Draw the detected text in green
#                 if detected_text[box_key]:
#                     text = detected_text[box_key]
#                     font = cv2.FONT_HERSHEY_SIMPLEX
#                     font_scale = 1  # Font size approximately 16
#                     font_thickness = 3
                    
#                     # Draw the text on the frame in green (233, 255, 110)
                    
#                     # cv2.putText(frame, text, (x1, y2 + 20), font, font_scale, (0,90,233), font_thickness)
#                     cvzone.putTextRect(frame, f"{text}", [x1 + 8, y1 - 12] ,thickness=2, scale=1.5)

#     # Display the frame
#     cv2.imshow('Frame', frame)

#     # Exit on 'q' key press
#     if cv2.waitKey(1) & 0xFF == ord('q'):
#         break

# # Release resources
# cap.release()
# cv2.destroyAllWindows()


