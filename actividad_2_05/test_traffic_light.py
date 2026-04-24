import cv2
import numpy as np
import sys
import os

# Añadir el path del módulo
sys.path.insert(0, os.path.dirname(__file__))

from actividad_2_05 import TrafficLightDetection

def test_with_simulator():
    """
    Prueba el detector de semáforos con el simulador 3DGS
    """
    import grpc
    import time
    
    # Importar los módulos gRPC del simulador
    sys.path.insert(0, '../actividad_2_04')
    import te3002b_pb2
    import te3002b_pb2_grpc
    import google.protobuf.empty_pb2
    
    # Conectar al simulador
    channel = grpc.insecure_channel('127.0.0.1:7072')
    stub = te3002b_pb2_grpc.TE3002BSimStub(channel)
    
    # Configurar simulador
    config = te3002b_pb2.ConfigurationData()
    config.resetRobot = True
    config.mode = 1
    config.cameraWidth = 360
    config.cameraHeight = 240
    config.resetCamera = False
    config.scene = 2026
    config.cameraLinear.x = 0
    config.cameraLinear.y = 0
    config.cameraLinear.z = 0
    config.cameraAngular.x = 0
    config.cameraAngular.y = 0
    config.cameraAngular.z = 0
    
    req = google.protobuf.empty_pb2.Empty()
    stub.SetConfiguration(config)
    config.resetRobot = False
    time.sleep(0.5)
    stub.SetConfiguration(config)
    
    # Posicionar el robot en el semáforo
    cmd = te3002b_pb2.CommandData()
    cmd.linear.x = -5.0
    cmd.linear.y = -6.0
    cmd.linear.z = 0.0
    cmd.angular.x = 0.0
    cmd.angular.y = 0.0
    cmd.angular.z = 1.5
    stub.SetCommand(cmd)
    time.sleep(0.5)
    
    # Crear detector
    detector = TrafficLightDetection()
    
    print("Detector de semáforos iniciado. Presiona Ctrl+C para salir.")
    print("Estados detectados:")
    
    try:
        while True:
            # Obtener frame del simulador
            result = stub.GetImageFrame(req)
            img_buffer = np.frombuffer(result.data, np.uint8)
            image = cv2.imdecode(img_buffer, cv2.IMREAD_COLOR)
            
            if image is not None:
                # Redimensionar
                image = cv2.resize(image, (320, 240), interpolation=cv2.INTER_LANCZOS4)
                
                # Detectar estado del semáforo
                state = detector.detect_state(image)
                
                # Mostrar resultado en la imagen
                color_map = {
                    'red': (0, 0, 255),
                    'yellow': (0, 255, 255),
                    'green': (0, 255, 0),
                    'none': (128, 128, 128)
                }
                
                color = color_map.get(state, (255, 255, 255))
                cv2.putText(image, f"State: {state.upper()}", (10, 30),
                           cv2.FONT_HERSHEY_SIMPLEX, 1, color, 2)
                
                # Mostrar imagen
                cv2.imshow('Traffic Light Detection', image)
                
                # Imprimir estado
                print(f"Frame {result.seq}: {state}")
            
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
            
            time.sleep(0.025)
    
    except KeyboardInterrupt:
        print("\nDeteniendo detector...")
    
    finally:
        cv2.destroyAllWindows()

def test_with_image(image_path):
    """
    Prueba el detector con una imagen estática
    """
    detector = TrafficLightDetection()
    
    image = cv2.imread(image_path)
    if image is None:
        print(f"Error: No se pudo cargar la imagen {image_path}")
        return
    
    state = detector.detect_state(image)
    print(f"Estado detectado: {state}")
    
    # Mostrar imagen con resultado
    color_map = {
        'red': (0, 0, 255),
        'yellow': (0, 255, 255),
        'green': (0, 255, 0),
        'none': (128, 128, 128)
    }
    
    color = color_map.get(state, (255, 255, 255))
    cv2.putText(image, f"State: {state.upper()}", (10, 30),
               cv2.FONT_HERSHEY_SIMPLEX, 1, color, 2)
    
    cv2.imshow('Traffic Light Detection', image)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

if __name__ == "__main__":
    if len(sys.argv) > 1:
        # Modo imagen
        test_with_image(sys.argv[1])
    else:
        # Modo simulador
        test_with_simulator()
