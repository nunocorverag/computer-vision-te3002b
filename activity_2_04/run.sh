#!/bin/bash
# Script helper para ejecutar los clientes del simulador TE3002B

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

# Verificar que el simulador esté corriendo
if ! nc -z 127.0.0.1 7072 2>/dev/null; then
    echo "⚠️  ADVERTENCIA: El simulador no parece estar corriendo en puerto 7072"
    echo "   Ejecuta primero: te3002b-sim"
    echo ""
fi

# Mostrar opciones
if [ -z "$1" ]; then
    echo "Uso: ./run.sh [opción]"
    echo ""
    echo "Opciones disponibles:"
    echo "  test      - Cliente de prueba básico (client-rpc-tester.py)"
    echo "  full      - Cliente autónomo con visión (fulltest.py)"
    echo "  ros2      - Puente ROS2 (client-ros2.py)"
    echo "  activity  - Actividad 2.04 (actividad_2_04.py)"
    echo ""
    echo "Ejemplo: ./run.sh full"
    exit 1
fi

case "$1" in
    test)
        python3 client-rpc-tester.py
        ;;
    full)
        python3 fulltest.py
        ;;
    ros2)
        python3 client-ros2.py
        ;;
    activity)
        python3 actividad_2_04.py
        ;;
    *)
        echo "❌ Opción no válida: $1"
        echo "Usa: test, full, ros2, o activity"
        exit 1
        ;;
esac
