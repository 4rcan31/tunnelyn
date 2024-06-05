#!/bin/bash

# Ruta a tu clave SSH
KEY_PATH="clave"

# Usuario y dirección IP de tu VPS
USER="root"
VPS_IP="34.16.227.83"

# Puerto remoto (VPS) y puerto local
REMOTE_PORT=222 #por defecto para conectarse por ssh
#el puerto 22 de la pc remota esta siendo ocupado para 
# hacer los tuneles, asi que no podemos ocupar el 22, por eso ocupamos el 22
LOCAL_PORT=22

# Establecer el túnel SSH
ssh -i "$KEY_PATH" -R "$REMOTE_PORT:localhost:$LOCAL_PORT" "$USER@$VPS_IP"
