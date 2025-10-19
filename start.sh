#!/bin/bash

VENV_PATH="venv"

if [ ! -d "$VENV_PATH" ]; then
    echo "Entorno virtual no encontrado. Creando..."
    python3 -m venv $VENV_PATH
fi

source $VENV_PATH/bin/activate

pip install -r requirements.txt

python src/main.py

