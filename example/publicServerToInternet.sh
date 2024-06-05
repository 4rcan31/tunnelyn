#!/bin/bash

# Ruta a tu clave SSH
KEY_PATH="clave"

# Usuario y dirección IP de tu VPS
USER="root"
VPS_IP="34.16.227.83"

# Puerto remoto (VPS) y puerto local
REMOTE_PORT=8081
LOCAL_PORT=80

# Establecer el túnel SSH
ssh -i "$KEY_PATH" -R "$REMOTE_PORT:localhost:$LOCAL_PORT" "$USER@$VPS_IP"
