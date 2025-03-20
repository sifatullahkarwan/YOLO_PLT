import gradio as gr
import sqlite3
import os
import cv2
import numpy as np
from datetime import datetime, timedelta
from ultralytics import YOLO
from sort.sort import Sort
import cvzone
from convertdate import persian
from PIL import Image
import io

# Database Path
DB_PATH = "./Database/screeb.db"

def gregorian_to_persian(gregorian_date):
    year, month, day = gregorian_date.year, gregorian_date.month, gregorian_date.day
    return persian.from_gregorian(year, month, day)

def fetch_data(days):
    """Fetch number plate data from the last N days and return images."""
    connection = sqlite3.connect(DB_PATH)
    cursor = connection.cursor()
    
    start_date = datetime.now() - timedelta(days=days)
    start_date_str = start_date.strftime('%Y-%m-%d')
    
    cursor.execute("""
        SELECT plate, entry_time, exit_time FROM number_plates
        WHERE entry_time >= ?
    """, (start_date_str,))
    
    records = cursor.fetchall()
    connection.close()
    
    if not records:
        return "No records found."
    
    results = []
    for plate_blob, entry, exit in records:
        hijri_entry = gregorian_to_persian(datetime.strptime(entry, '%Y-%m-%d %H:%M:%S'))
        entry_time = f"{hijri_entry[0]}-{hijri_entry[1]:02d}-{hijri_entry[2]:02d} {entry.split()[1]}"
        
        if exit:
            hijri_exit = gregorian_to_persian(datetime.strptime(exit, '%Y-%m-%d %H:%M:%S'))
            exit_time = f"{hijri_exit[0]}-{hijri_exit[1]:02d}-{hijri_exit[2]:02d} {exit.split()[1]}"
        else:
            exit_time = "N/A"
        
        image = Image.open(io.BytesIO(plate_blob))
        # resized_img = image.resize((45,45))
        results.append((image, f"Entry: {entry_time}, Exit: {exit_time}"))
    
    return results

def run_detection():
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        return "Error: Video not found or cannot be opened."
    
    connection = sqlite3.connect(DB_PATH)
    cursor = connection.cursor()
    
    model = YOLO('runs/detect/train6/weights/best.pt')
    tracker = Sort(max_age=10, min_hits=2, iou_threshold=0.3)
    tracked_plates = {}
    
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        
        results = model(frame)
        detections = []
        
        for info in results:
            for box in info.boxes:
                x1, y1, x2, y2 = map(int, box.xyxy[0])
                confidence = float(box.conf[0]) * 100
                if confidence > 80:
                    detections.append([x1, y1, x2, y2, confidence])
        
        detections = np.array(detections) if detections else np.empty((0, 5))
        tracked_objects = tracker.update(detections)
        current_ids = set()
        
        for obj in tracked_objects:
            x1, y1, x2, y2, track_id = map(int, obj)
            current_ids.add(track_id)
            
            if track_id not in tracked_plates:
                entry_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                plate_image = frame[y1:y2, x1:x2]
                
                if plate_image.size > 0:
                    _, buffer = cv2.imencode(".jpg", plate_image)
                    plate_blob = buffer.tobytes()
                    
                    cursor.execute('''INSERT INTO number_plates (plate, entry_time, exit_time)
                                    VALUES (?, ?, NULL)''', (plate_blob, entry_time))
                    connection.commit()
                    
                    tracked_plates[track_id] = {"entry_time": entry_time}
        
        lost_ids = set(tracked_plates.keys()) - current_ids
        for lost_id in lost_ids:
            if "exit_time" not in tracked_plates[lost_id]:
                exit_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                cursor.execute('''UPDATE number_plates SET exit_time = ? WHERE entry_time = ?''', 
                               (exit_time, tracked_plates[lost_id]["entry_time"]))
                connection.commit()
                tracked_plates[lost_id]["exit_time"] = exit_time
        
        cv2.imshow('Frame', frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    
    cap.release()
    cv2.destroyAllWindows()
    connection.close()
    return "Detection completed!"

def open_database_ui():
    os.system(f'sqlitebrowser "{os.path.abspath(DB_PATH)}" &')
    return "Opening Database UI."

gui = gr.Blocks()
with gui:
    gr.Markdown("<h2 style='text-align: center;'>دافغانستان د موترونو د نمبر پلیتو د تشخیص سیستم</h2>")
    
    with gr.Row():
        run_btn = gr.Button("شناسایی نمبر پلیت")
        db_btn = gr.Button("دیتابیس ها")
    
    output_text = gr.Textbox(label="Output", interactive=False)
    plate_display = gr.Gallery(label="نمبر پلیت شناسایی شده")
    
    with gr.Row(visible=False) as filter_buttons:
        last_week_btn = gr.Button("دیتا هفته قبل")
        last_2_weeks_btn = gr.Button("دیتا۲ هفته قبل")
        last_3_weeks_btn = gr.Button("دیتا ۳ هفته قبل")
        all_database = gr.Button('دیتابیس')
    
    db_btn.click(lambda: ("Select a date range:", gr.update(visible=True)), outputs=[output_text, filter_buttons])
    last_week_btn.click(lambda: fetch_data(7), outputs=plate_display)
    last_2_weeks_btn.click(lambda: fetch_data(14), outputs=plate_display)
    last_3_weeks_btn.click(lambda: fetch_data(21), outputs=plate_display)
    run_btn.click(run_detection, outputs=output_text)
    all_database.click(open_database_ui)

gui.launch(debug=True)