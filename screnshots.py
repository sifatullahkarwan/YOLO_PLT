import cv2
import sqlite3
import os
import numpy as np
from datetime import datetime
from ultralytics import YOLO
from sort.sort import Sort
import cvzone

# Connect to SQLite database
connections_db = sqlite3.connect('./Database/screeb.db')
cursor = connections_db.cursor()

# Create table for number plates
cursor.execute('''
CREATE TABLE IF NOT EXISTS number_plates (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    plate BLOB NOT NULL,
    entry_time TEXT NOT NULL,
    exit_time TEXT
);
''')
connections_db.commit()

# Load YOLO model
model = YOLO('runs/detect/train6/weights/best.pt')
classnames = ['Plate_detected']

# Create screenshots directory if it doesn't exist
if not os.path.exists('screenshots'):
    os.makedirs('screenshots')

# Initialize SORT tracker
tracker = Sort(max_age=10, min_hits=2, iou_threshold=0.3)

tracked_plates = {}  # Store plate info by tracker ID (track_id -> {"entry_time": ..., "exit_time": ...})

def smooth_image(image):
    """Apply Gaussian Blur for smoothing"""
    return cv2.GaussianBlur(image, (5, 5), 0)

# Initialize camera
cap = cv2.VideoCapture(0)

while True:
    ret, frame = cap.read()  # Read frame from the camera
    if not ret:
        break

    frame = cv2.resize(frame, (1080, 720))

    # Smooth the image for better detection
    frame = smooth_image(frame)

    # Run YOLO model on the frame
    results = model(frame)

    detections = []

    # Process detections with confidence check
    for info in results:
        for box in info.boxes:
            x1, y1, x2, y2 = map(int, box.xyxy[0])
            confidence = float(box.conf[0]) * 100  # Confidence is kept but now used for decision

            # Insert data only if confidence is greater than 60
            if confidence > 60:
                detections.append([x1, y1, x2, y2, confidence])

    detections = np.array(detections) if detections else np.empty((0, 5))
    tracked_objects = tracker.update(detections)

    current_ids = set()  # Keep track of active track IDs in this frame

    for obj in tracked_objects:
        x1, y1, x2, y2, track_id = map(int, obj)
        current_ids.add(track_id)

        # Draw bounding box and ID
        cvzone.cornerRect(frame, (x1, y1, x2-x1, y2-y1), l=20, rt=2, colorR=(0, 255, 0))
        cvzone.putTextRect(frame, f"ID {track_id}", (x1, y1 - 10),
                    thickness=2, scale=1.5)

        # If plate is new, save it
        if confidence > 80:
            if track_id not in tracked_plates:
                entry_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                plate_image = frame[y1:y2, x1:x2]
                screenshot_path = f'screenshots/plate_{track_id}.jpg'
                cv2.imwrite(screenshot_path, plate_image)

                with open(screenshot_path, 'rb') as file:
                    plate_blob = file.read()

                cursor.execute('''INSERT INTO number_plates (plate, entry_time, exit_time)
                                VALUES (?, ?, ?)''', (plate_blob, entry_time, None))
                connections_db.commit()

            tracked_plates[track_id] = {"entry_time": entry_time, "exit_time": None}

    # Find plates that are no longer in tracking
    lost_ids = set(tracked_plates.keys()) - current_ids

    for lost_id in lost_ids:
        if tracked_plates[lost_id]["exit_time"] is None:  # If exit time is not set
            exit_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

            # Update database
            cursor.execute('''UPDATE number_plates 
                              SET exit_time = ? 
                              WHERE entry_time = ?''', 
                           (exit_time, tracked_plates[lost_id]["entry_time"]))
            connections_db.commit()

            # Update local dictionary
            tracked_plates[lost_id]["exit_time"] = exit_time

    # Display the frame
    cv2.imshow('Frame', frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release resources
cap.release()
cv2.destroyAllWindows()
connections_db.close()
