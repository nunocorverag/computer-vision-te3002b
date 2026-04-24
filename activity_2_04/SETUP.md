# Guía Rápida - Simulador TE3002B

## 📍 Ubicación del Simulador
El simulador está instalado en:
```
~/.local/share/te3002b-simulator/LinuxCtrl/
```

## 🚀 Cómo Ejecutar

### 1. Iniciar el Simulador
Desde cualquier ubicación, ejecuta:
```bash
te3002b-sim
```

El simulador quedará escuchando en `127.0.0.1:7072`

### 2. Ejecutar Clientes Python

Desde este directorio (`Puzzlebot-Track-Simulator-Repo/`):

```bash
# Cliente de prueba básico
./run.sh test

# Cliente autónomo completo con visión
./run.sh full

# Puente ROS2 (requiere ROS2 configurado)
./run.sh ros2

# Actividad 2.04
./run.sh activity
```

### Alternativa: Ejecución manual
```bash
# Activar entorno virtual
source venv/bin/activate

# Ejecutar cualquier script
python3 fulltest.py
python3 client-rpc-tester.py
```

## 📦 Dependencias Instaladas

El entorno virtual `venv/` incluye:
- `grpcio` - Comunicación gRPC
- `protobuf` - Serialización de mensajes
- `opencv-python` - Procesamiento de imágenes
- `numpy` - Operaciones numéricas

## 🔧 Troubleshooting

**Error: "UNAVAILABLE: failed to connect"**
- Asegúrate de que el simulador esté corriendo primero con `te3002b-sim`

**Error: "ModuleNotFoundError"**
- Activa el entorno virtual: `source venv/bin/activate`

**Error: "Permission denied"**
- Dale permisos de ejecución: `chmod +x run.sh`

## 📝 Notas
- El simulador debe estar corriendo **antes** de ejecutar cualquier cliente
- Los scripts usan el entorno virtual automáticamente
- Frecuencia de control: ~40 Hz (25ms por frame)
