# import cv2
# import sqlite3
# from datetime import datetime
# from ultralytics import YOLO
# import os

# # Connect to SQLite database
# connections_db = sqlite3.connect('./Database/plate_detected.db')
# cursor = connections_db.cursor()

# # Create table for number plates
# cursor.execute('''
# CREATE TABLE IF NOT EXISTS number_plates (
#     id INTEGER PRIMARY KEY AUTOINCREMENT,
#     plate BLOB NOT NULL,
#     entry_time TEXT NOT NULL,
#     exit_time TEXT
# );
# ''')
# connections_db.commit()

# # Load video
# video_path = 0  # Use webcam or video file
# cap = cv2.VideoCapture(video_path)

# # Load YOLO model
# model = YOLO('runs/detect/train6/weights/best.pt')
# classnames = ['Plate_detected']

# # Create screenshots directory if it doesn't exist
# if not os.path.exists('screenshots'):
#     os.makedirs('screenshots')

# counter = 0
# tracked_plates = {}

# while True:
#     ret, frame = cap.read()
#     if not ret:
#         break

#     frame = cv2.resize(frame, (1080, 720))
#     results = model(frame)

#     current_plates = set()

#     for info in results:
#         parameters = info.boxes
#         for box in parameters:
#             x1, y1, x2, y2 = map(int, box.xyxy[0])
#             confidence = float(box.conf[0]) * 100  # Convert to percentage
#             class_detect = int(box.cls[0])
#             class_detect = classnames[class_detect]

#             # Insert into DB only if confidence > 60%
#             # Draw bounding box
#             cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 244, 0), 2)

#             # Add text label with pink background
#             label = f"{class_detect} ({confidence:.1f}%)"
#             (text_width, text_height), baseline = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 2)
#             cv2.rectangle(frame, (x1, y1 - text_height - 5), (x1 + text_width, y1), (147, 20, 255), -1)  # Pink background
#             cv2.putText(frame, label, (x1, y1 - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)  # White text

#             # Crop detected plate region
#             plate_image = frame[y1:y2, x1:x2]
#             if confidence > 80:  # Only save screenshot if confidence is greater than 90%
#                 screenshot_path = f'screenshots/plate_{counter}.jpg'
#                 cv2.imwrite(screenshot_path, plate_image)
#                 counter += 1

#                 # Save plate image and data to database if confidence > 86%
#                 entry_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
#                 with open(screenshot_path, 'rb') as file:
#                     plate_blob = file.read()
#                 if confidence > 80:  # Insert data into the DB if confidence > 86%
#                     cursor.execute(''' INSERT INTO number_plates (plate, entry_time, exit_time)
#                     VALUES (?, ?, ?)
#                     ''', (plate_blob, entry_time, None))  # Set exit_time to None initially
#                     connections_db.commit()

#             # Track plate by its bounding box coordinates
#             current_plates.add((x1, y1, x2, y2))

#     # Check for plates that were previously detected but are now missing
#     for plate in list(tracked_plates.keys()):
#         if plate not in current_plates:
#             exit_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
#             # Update exit_time in the database when the plate is no longer detected
#             cursor.execute('''
#             UPDATE number_plates
#             SET exit_time = ?
#             WHERE entry_time = ?
#             ''', (exit_time, tracked_plates[plate]))
#             connections_db.commit()
#             del tracked_plates[plate]

#     # Update tracked plates
#     for plate in current_plates:
#         if plate not in tracked_plates:
#             tracked_plates[plate] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

#     # Display the frame
#     cv2.imshow('Frame', frame)

#     # Exit on 'q' key press
#     if cv2.waitKey(1) & 0xFF == ord('q'):
#         break

# # Release resources
# cap.release()
# cv2.destroyAllWindows()
# connections_db.close()
