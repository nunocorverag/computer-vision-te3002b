import cv2
import numpy as np
import pickle

cap = cv2.VideoCapture('./actividad-2-01/video.mp4')

if not cap.isOpened():
    print("Error al abrir el video")
    exit()

def get_frame(cap, n):
    cap.set(cv2.CAP_PROP_POS_FRAMES, n)
    ret, frame = cap.read()
    return frame if ret else None

# Frame 10 - Scale 1.5x
frame = get_frame(cap, 9)
frame_10 = cv2.resize(frame, None, fx=1.5, fy=1.5)
cv2.imwrite('frame_10.png', frame_10)

# Frame 30 - Scale 0.5x
frame = get_frame(cap, 29)
frame_30 = cv2.resize(frame, None, fx=0.5, fy=0.5)
cv2.imwrite('frame_30.png', frame_30)

# Frame 50 - Rotate 35 degrees
frame = get_frame(cap, 49)
h, w = frame.shape[:2]
cx, cy = w / 2.0, h / 2.0
angulo = np.radians(35)
cos_a = np.cos(angulo)
sin_a = np.sin(angulo)

# Construir como M2 @ R @ M1
M1 = np.array([
    [1.0, 0.0, -cx],
    [0.0, 1.0, -cy],
    [0.0, 0.0, 1.0]
], dtype=np.float64)

R = np.array([
    [ cos_a, sin_a, 0.0],
    [-sin_a, cos_a, 0.0],
    [ 0.0,   0.0,   1.0]
], dtype=np.float64)

M2 = np.array([
    [1.0, 0.0, cx],
    [0.0, 1.0, cy],
    [0.0, 0.0, 1.0]
], dtype=np.float64)

M = M2 @ R @ M1
frame_50 = cv2.warpAffine(frame, M[:2], (w, h))
cv2.imwrite('frame_50.png', frame_50)

# Guardar la 3x3 completa
with open('rotation_matrix.pkl', 'wb') as f:
    pickle.dump(M, f)

# Frame 70 - Horizontal flip
frame = get_frame(cap, 69)
frame_70 = cv2.flip(frame, 1)
cv2.imwrite('frame_70.png', frame_70)

cap.release()