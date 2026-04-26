import cv2
from threading import Thread
import time
import numpy as np

class VideoStream:
    def __init__(self, source=0):
        self.stream = cv2.VideoCapture(source)
        (self.grabbed, self.frame) = self.stream.read()
        self.stopped = False

    def start(self):
        Thread(target=self.update, args=()).start()
        return self

    def update(self):
        while True:
            if self.stopped:
                return
            (self.grabbed, self.frame) = self.stream.read()
            if not self.grabbed:
                self.stopped = True
                break

    def read(self):
        return self.frame

    def stop(self):
        self.stopped = True
        if self.stream.isOpened():
            self.stream.release()

def get_dominant_color(frame, bbox):
    """
    Determina un color predominante básico para el bounding box.
    """
    x1, y1, x2, y2 = map(int, bbox)
    roi = frame[y1:y2, x1:x2]
    if roi.size == 0:
        return "unknown"
    
    # Promedio de colores BGR
    avg_color = np.mean(roi, axis=(0, 1))
    b, g, r = avg_color
    
    # Lógica simple de decisión
    if r > g + 20 and r > b + 20: return "red"
    if g > r + 20 and g > b + 20: return "green"
    if b > r + 20 and b > g + 20: return "blue"
    if r > 200 and g > 200 and b > 200: return "white"
    if r < 50 and g < 50 and b < 50: return "black"
    
    return "gray"
