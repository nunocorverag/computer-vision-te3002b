import time
from coppeliasim_zmqremoteapi_client import RemoteAPIClient
import cv2
import numpy as np

# Conectar al API
client = RemoteAPIClient()
sim = client.getObject('sim')

# Obtener handle de la cámara
sensor1Handle = sim.getObject('/Vision_sensor')

# Iniciar simulación
sim.startSimulation()

# Esperar 2 segundos
time.sleep(2)

# Capturar imagen
img, [resX, resY] = sim.getVisionSensorImg(sensor1Handle)
img = np.frombuffer(img, dtype=np.uint8).reshape(resY, resX, 3)

# Corregir orientación y color
img = cv2.flip(img, 0)
img_bgr = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)

# Guardar
cv2.imwrite('resultado.png', img_bgr)

# Detener simulación
sim.stopSimulation()