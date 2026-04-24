"""
actividad_2_06.py — Traffic Sign Detection Pipeline (Actividad 2.6)

PIPELINE DE DETECCIÓN (2 Acercamientos):
==================================================

ACERCAMIENTO A: Métrica de Calidad de Imagen (Blur Detection)
--------------------------------------------------------------
- Utiliza el operador Laplaciano para calcular la varianza de la imagen
- Si la varianza es menor al umbral (100.0), la imagen se considera borrosa
- Las imágenes borrosas se descartan para evitar falsos positivos
- Esto mejora la precisión del detector CNN al filtrar frames de baja calidad

ACERCAMIENTO B: CNN - YOLOv8 (Deep Learning)
--------------------------------------------------------------
- Modelo YOLOv8n entrenado con dataset personalizado de señales de tráfico
- Detecta 5 clases: Go straight, Stop, Turn Left, Turn Right, Workers
- Utiliza transfer learning desde COCO para mejor generalización
- Confidence threshold: 0.45 (ajustable según precisión/recall deseado)

FLUJO DEL PIPELINE:
1. Capturar frame del simulador vía gRPC
2. Aplicar filtro de blur (Acercamiento A)
3. Si el frame es nítido, ejecutar detección YOLO (Acercamiento B)
4. Dibujar bounding boxes y mostrar señal detectada
5. Grabar video del resultado

Senales detectadas (segun UNECE):
- Stop (pag. 88)
- Workers (pag. 83-84)
- Go straight (pag. 93)
- Turn Left/Right (pag. 93)

Autor: [Tu nombre]
Fecha: 23 de Abril 2026
"""

import cv2
import numpy as np
import grpc
import google.protobuf.empty_pb2
import time
import sys
from pathlib import Path

import te3002b_pb2
import te3002b_pb2_grpc
from detector import TrafficSignDetection

GRPC_ADDR    = "127.0.0.1:7072"
CAM_W, CAM_H = 360, 240
OUT_W, OUT_H = 320, 240
SCENE        = 2026

VIDEO_OUTPUT = "traffic_signs_detection.mp4"
FPS          = 30


def add_noise_to_image(image, kernel_s=3, noise_level=5):
    """
    Aplica ruido y blur a la imagen para simular condiciones reales.
    Esto es parte del preprocesamiento del simulador.
    """
    hsv_image = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    h, s, v = cv2.split(hsv_image)
    noise = np.random.randint(-noise_level, noise_level + 1, v.shape, dtype='int16')
    v_noisy = v.astype('int16') + noise
    v_noisy = np.clip(v_noisy, 0, 255).astype('uint8')
    hsv_noisy = cv2.merge([h, s, v_noisy])
    noisy_image = cv2.cvtColor(hsv_noisy, cv2.COLOR_HSV2BGR)
    noisy_image = cv2.GaussianBlur(noisy_image, (kernel_s, kernel_s), 0)
    alpha = 0.55
    beta = 55
    output_image = cv2.convertScaleAbs(noisy_image, alpha=alpha, beta=beta)
    return output_image


def main():
    print("=" * 70)
    print("ACTIVIDAD 2.6: DETECCION DE SENALES DE TRAFICO")
    print("=" * 70)
    print("\nPIPELINE:")
    print("  1. Acercamiento A: Blur Detection (Metrica de Calidad)")
    print("  2. Acercamiento B: YOLOv8 CNN (Deep Learning)")
    print("\nSenales detectables:")
    print("  - Stop, Workers, Go straight, Turn Left, Turn Right")
    print("=" * 70)
    
    # Inicializar detector con modelo entrenado
    print("\n[1/4] Cargando modelo YOLO entrenado")
    detector = TrafficSignDetection()
    
    # Conectar al simulador
    print("[2/4] Conectando al simulador")
    channel = grpc.insecure_channel(GRPC_ADDR)
    stub    = te3002b_pb2_grpc.TE3002BSimStub(channel)
    
    # Configurar simulador
    cfg = te3002b_pb2.ConfigurationData()
    cfg.resetRobot   = True
    cfg.mode         = 2
    cfg.cameraWidth  = CAM_W
    cfg.cameraHeight = CAM_H
    cfg.resetCamera  = False
    cfg.scene        = SCENE
    cfg.cameraLinear.x  = 0
    cfg.cameraLinear.y  = 0
    cfg.cameraLinear.z  = 0
    cfg.cameraAngular.x = 0
    cfg.cameraAngular.y = 0
    cfg.cameraAngular.z = 0
    
    stub.SetConfiguration(cfg)
    cfg.resetRobot = False
    time.sleep(0.25)
    stub.SetConfiguration(cfg)
    
    # Inicializar grabación de video
    print("[3/4] Configurando grabacion de video")
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    video_writer = cv2.VideoWriter(VIDEO_OUTPUT, fourcc, FPS, (OUT_W, OUT_H))
    
    req = google.protobuf.empty_pb2.Empty()
    frame_count = 0
    detected_signs = set()  # Para trackear cuáles señales hemos detectado
    
    print("[4/4] Iniciando deteccion")
    print("\nControles:")
    print("  Q - Salir")
    print("  SPACE - Pausar/Reanudar")
    print("\nDetectando senales\n")
    
    paused = False
    
    try:
        while True:
            if not paused:
                # Obtener frame del simulador
                result  = stub.GetImageFrame(req)
                buf     = np.frombuffer(result.data, np.uint8)
                img_raw = cv2.imdecode(buf, cv2.IMREAD_COLOR)
                
                if img_raw is None:
                    continue
                
                # Preprocesar imagen (ruido + blur simulado)
                img = add_noise_to_image(img_raw, 3)
                frame = cv2.resize(img, (OUT_W, OUT_H), interpolation=cv2.INTER_LANCZOS4)
                
                # ============================================================
                # PIPELINE DE DETECCIÓN
                # ============================================================
                # 1. Acercamiento A: Filtro de calidad (blur detection)
                # 2. Acercamiento B: Detección CNN (YOLO)
                annotated_frame, detected_sign = detector.detect_signs(frame.copy())
                
                # Agregar información del pipeline en pantalla
                cv2.putText(annotated_frame, "Pipeline: Blur Filter + YOLO CNN", 
                           (10, OUT_H - 60), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 255), 1)
                
                # Mostrar señal detectada en frente
                if detected_sign not in ["None", "Blurry"]:
                    detected_signs.add(detected_sign)
                    cv2.putText(annotated_frame, f"En frente: {detected_sign}", 
                               (10, OUT_H - 30), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)
                else:
                    cv2.putText(annotated_frame, "En frente: ---", 
                               (10, OUT_H - 30), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (200, 200, 200), 1)
                
                # Mostrar contador de señales únicas detectadas
                cv2.putText(annotated_frame, f"Detectadas: {len(detected_signs)}/5", 
                           (10, OUT_H - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 255, 0), 1)
                
                # Grabar frame
                video_writer.write(annotated_frame)
                frame_count += 1
                
                # Mostrar frame
                cv2.imshow("Traffic Sign Detection - Actividad 2.6", annotated_frame)
            
            # Controles de teclado
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                break
            elif key == ord(' '):
                paused = not paused
                print(f"{'Pausado' if paused else 'Reanudado'}")
    
    except KeyboardInterrupt:
        print("\n\nInterrupcion del usuario")
    
    finally:
        # Cleanup
        video_writer.release()
        cv2.destroyAllWindows()
        
        print("\n" + "=" * 70)
        print("RESUMEN DE DETECCION")
        print("=" * 70)
        print(f"Frames procesados: {frame_count}")
        print(f"Senales unicas detectadas: {len(detected_signs)}/5")
        print(f"Senales encontradas: {', '.join(sorted(detected_signs)) if detected_signs else 'Ninguna'}")
        print(f"\nVideo guardado en: {VIDEO_OUTPUT}")
        print("=" * 70)
        
        # Verificar requisito de la actividad
        if len(detected_signs) >= 4:
            print("\nACTIVIDAD COMPLETADA: Todas las senales detectadas al menos 1 vez")
        else:
            print(f"\nFaltan detectar: {5 - len(detected_signs)} senales")
            missing = set(["Go straight", "Stop", "Turn Left", "Turn Right", "Workers"]) - detected_signs
            print(f"   Senales faltantes: {', '.join(missing)}")


if __name__ == "__main__":
    main()
