#!/bin/bash

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Activar entorno virtual (buscar .venv o venv)
if [ -d ".venv" ]; then
    source .venv/bin/activate
elif [ -d "venv" ]; then
    source venv/bin/activate
else
    echo "❌ Error: No se encontró entorno virtual (.venv o venv)"
    echo "   Ejecuta primero: ./setup_venv.sh"
    exit 1
fi

if ! nc -z 127.0.0.1 7072 2>/dev/null; then
    echo "⚠️  ADVERTENCIA: El simulador no parece estar corriendo en puerto 7072"
    echo "   Ejecuta primero: te3002b-sim"
    echo ""
fi

if [ -z "$1" ]; then
    echo "Uso: ./run.sh [opción]"
    echo ""
    echo "Opciones disponibles:"
    echo "  test      - Solo detector de semáforo (sin movimiento)"
    echo "  robot     - Robot con seguimiento de línea y semáforo"
    echo "  find      - Recorrer circuito mostrando posición (para encontrar semáforo)"
    echo "  image     - Probar con una imagen (requiere ruta como segundo argumento)"
    echo ""
    echo "Ejemplo: ./run.sh robot"
    echo "Ejemplo: ./run.sh test"
    echo "Ejemplo: ./run.sh find"
    echo "Ejemplo: ./run.sh image ruta/imagen.jpg"
    exit 1
fi

case "$1" in
    test)
        python3 test_traffic_light.py
        ;;
    robot)
        python3 robot_with_traffic_light.py
        ;;
    find)
        python3 find_traffic_light_position.py
        ;;
    image)
        if [ -z "$2" ]; then
            echo "❌ Error: Debes proporcionar la ruta de la imagen"
            echo "Ejemplo: ./run.sh image ruta/imagen.jpg"
            exit 1
        fi
        python3 test_traffic_light.py "$2"
        ;;
    *)
        echo "❌ Opción no válida: $1"
        echo "Usa: test, robot, find o image"
        exit 1
        ;;
esac
