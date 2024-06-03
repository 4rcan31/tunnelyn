#!/bin/bash

sudo apt install -y openssh-server openssh-client
SSHD_CONFIG="/etc/ssh/sshd_config"
BACKUP_DIR="/etc/ssh/backup"
mkdir -p "$BACKUP_DIR"
DATE=$(date +"%Y-%m-%d")
HOUR=$(date +"%H-%M-%S")
LETTERS=(A B C D E F G H I J K L M N O P Q R S T U V W X Y Z)
COUNT=1

# Hacer una copia de seguridad del archivo sshd_config original
BACKUP_FILE="$BACKUP_DIR/sshd_config-$DATE-$HOUR-${LETTERS[COUNT]}.bak"
while [ -e "$BACKUP_FILE" ]; do
    ((COUNT++))
    BACKUP_FILE="$BACKUP_DIR/sshd_config-$DATE-$HOUR-${LETTERS[COUNT]}.bak"
done
cp "$SSHD_CONFIG" "$BACKUP_FILE"

# Claves que se desean activar
KEYS=(
    "AllowTcpForwarding"
    "GatewayPorts"
    "X11Forwarding"
)

# Descomentar las claves necesarias en el archivo sshd_config
for key in "${KEYS[@]}"; do
    sed -i "s/#\?\($key\s*\).*/\1yes/" "$SSHD_CONFIG"
done


systemctl restart sshd
