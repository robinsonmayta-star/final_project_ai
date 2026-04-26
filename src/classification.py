import os
import glob
import time
from datetime import datetime
import cv2
import pandas as pd
import numpy as np
from ultralytics import YOLO
from utils.camera_utils import VideoStream

def get_position_region(cx_norm, cy_norm):
    """Determina la región de la imagen (top, middle, bottom) x (left, center, right)"""
    row = "middle"
    if cy_norm < 0.33: row = "top"
    elif cy_norm > 0.66: row = "bottom"
    col = "center"
    if cx_norm < 0.33: col = "left"
    elif cx_norm > 0.66: col = "right"
    return f"{row}-{col}"

def get_rich_color(frame, coords):
    """Obtiene el color dominante y sus componentes RGB"""
    try:
        x1, y1, x2, y2 = map(int, coords)
        roi = frame[y1:y2, x1:x2]
        if roi.size == 0: return "unknown", 0, 0, 0
        avg_color = np.average(np.average(roi, axis=0), axis=0)
        b, g, r = map(int, avg_color)
        if r > g and r > b: name = "red"
        elif g > r and g > b: name = "green"
        elif b > r and b > g: name = "blue"
        elif r > 200 and g > 200 and b > 200: name = "white"
        elif r < 50 and g < 50 and b < 50: name = "black"
        else: name = "gray"
        return name, r, g, b
    except Exception: # pylint: disable=broad-exception-caught
        return "unknown", 0, 0, 0

def load_env(filepath="config.env"):
    """Carga variables de entorno con encoding explícito"""
    config = {}
    if os.path.exists(filepath):
        with open(filepath, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#"):
                    key, value = line.split("=", 1)
                    config[key.strip()] = value.strip()
    return config

# Configuración global
CONFIG = load_env()
MODEL_PATH = CONFIG.get("MODEL_PATH", "yolov8n.pt")
STAGING_DIR = CONFIG.get("STAGING_DIR", "data/staging")
CONF_THRESHOLD = float(CONFIG.get("CONFIDENCE_THRESHOLD", 0.4))
WINDOW_SECONDS = int(CONFIG.get("WINDOW_SECONDS", 10))

def extract_attributes(model, frame, results, source_type, source_id, frame_id, fps=30):
    """Extrae atributos enriquecidos según Sección 6"""
    detections = []
    f_h, f_w = frame.shape[:2]
    frame_area = f_h * f_w
    for r in results:
        for box in r.boxes:
            coords = box.xyxy[0].tolist()
            x1, y1, x2, y2 = coords
            w, h = x2 - x1, y2 - y1
            area_px = w * h
            cx, cy = x1 + (w/2), y1 + (h/2)
            cx_norm, cy_norm = cx / f_w, cy / f_h
            c_name, dr, dg, db = get_rich_color(frame, coords)
            det_id = f"{source_id}_{frame_id}_{int(box.cls[0])}_{int(time.time()*1000)}"
            detections.append({
                "source_type": source_type, "source_id": source_id, "frame_number": frame_id,
                "class_id": int(box.cls[0]), "class_name": model.names[int(box.cls[0])],
                "confidence": float(box.conf[0]), "x_min": x1, "y_min": y1, "x_max": x2, "y_max": y2,
                "width": w, "height": h, "area_pixels": area_px, "frame_width": f_w, "frame_height": f_h,
                "bbox_area_ratio": area_px / frame_area, "center_x": cx, "center_y": cy,
                "center_x_norm": cx_norm, "center_y_norm": cy_norm,
                "position_region": get_position_region(cx_norm, cy_norm),
                "dominant_color_name": c_name, "dom_r": dr, "dom_g": dg, "dom_b": db,
                "timestamp_sec": frame_id / fps if source_type == "video" else 0,
                "ingestion_date": datetime.now().isoformat(), "detection_id": det_id
            })
    return detections

def run_classification():
    """Ejecuta el pipeline de clasificación"""
    model = YOLO(MODEL_PATH)
    today = datetime.now().strftime("%Y%m%d")
    output_path = os.path.join(STAGING_DIR, today)
    os.makedirs(output_path, exist_ok=True)
    img_files = glob.glob("data/raw/images/*.jpeg")
    if img_files:
        all_imgs = []
        for img_p in img_files:
            frame = cv2.imread(img_p) # pylint: disable=no-member
            if frame is None: continue
            res = model(frame, verbose=False, conf=CONF_THRESHOLD)
            all_imgs.extend(extract_attributes(model, frame, res, "image", os.path.basename(img_p), 0))
        if all_imgs:
            pd.DataFrame(all_imgs).to_csv(os.path.join(output_path, f"detections_images_{int(time.time())}.csv"), index=False)
    vid_files = glob.glob("data/raw/videos/*.mp4")
    for vid_p in vid_files:
        vs = VideoStream(source=vid_p)
        if not vs.grabbed: continue
        vs.start()
        detections, start_time, frame_count = [], time.time(), 0
        fps = vs.stream.get(cv2.CAP_PROP_FPS) or 30 # pylint: disable=no-member
        while not vs.stopped:
            frame = vs.read()
            if frame is None: break
            frame_count += 1
            res = model(frame, verbose=False, conf=CONF_THRESHOLD)
            detections.extend(extract_attributes(model, frame, res, "video", os.path.basename(vid_p), frame_count, fps))
            if time.time() - start_time >= WINDOW_SECONDS:
                if detections:
                    pd.DataFrame(detections).to_csv(os.path.join(output_path, f"detections_{os.path.basename(vid_p)}_{int(time.time())}.csv"), index=False)
                    detections = []
                start_time = time.time()
        if detections:
            pd.DataFrame(detections).to_csv(os.path.join(output_path, f"detections_{os.path.basename(vid_p)}_final.csv"), index=False)
        vs.stop()

if __name__ == "__main__":
    run_classification()
