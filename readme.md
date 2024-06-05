# Configuración de Tunnel SSH

¡Hola! Este proyecto está diseñado para ayudarte a sacar a internet un servidor local a través de un VPS, evitando así el molesto CGNAT de tu ISP residencial sin tener que contratar un costoso internet dedicado. En lugar de gastar más de 100 dólares al mes, puedes optar por un VPS más económico en AWS, GCP, DigitalOcean o cualquier otro proveedor que permita crear un VPS. Este VPS servirá como redirección del tráfico, aprovechando su dirección IP pública para enviar todo el tráfico a tu máquina local.

## Configuración del VPS

Primero, necesitamos configurar nuestro VPS para que pueda recibir port forwarding. Para esto, instalamos SSH en nuestro servidor y configuramos `sshd` para que acepte conexiones mediante llaves. Debes habilitar y descomentar las siguientes reglas en el archivo de configuración SSH (`/etc/ssh/sshd_config`):

```sh
AllowTcpForwarding yes
GatewayPorts yes
X11Forwarding yes
```

Si necesitas un ejemplo de cómo debería quedar tu configuración SSH, revisa el archivo `ssh_vps_config/sshd_config`. Para ahorrarte tiempo, puedes ejecutar el script `ssh_vps_config/install.sh` siguiendo estos pasos:

1. Darle permisos de ejecución:
    ```sh
    sudo chmod +x ssh_vps_config/install.sh
    ```
2. Ejecutarlo:
    ```sh
    sudo ./ssh_vps_config/install.sh
    ```

Este script simplemente activará las tres reglas mencionadas antes. Recuerda configurar el servicio SSH para que use llaves en lugar de contraseñas.

¡Y listo! Ahora tienes tu servidor SSH configurado en tu VPS. No olvides revisar el firewall del VPS para abrir los puertos necesarios.

## Configuración del Servidor Local para Abrir Puertos

Con el VPS configurado, es hora de abrir puertos en tu servidor local usando el pequeño programa CLI `jenu.py`. Este programa te permitirá manejar la apertura, cierre y lectura de los puertos que necesitas.

### Confiar en el Host (Primera Vez)

La primera vez que te conectes por SSH, tu máquina local pedirá confirmación de confianza. Ejecuta:

```sh
python3 jenu.py -k clave -v 234.322.3.12 --verify
```

Si esto no funciona, conéctate manualmente una vez por SSH para verificar la confiabilidad:

```sh
ssh -i clave root@234.322.3.12
```

### Abrir Puertos

Para abrir puertos, ejecuta:

```sh
python3 jenu.py -k clave -f 80:8081 -v 234.322.3.12
```

Esto forwardeará el puerto 80 de tu máquina local al puerto 8081 del VPS. Alternativamente, puedes usar la forma extendida del comando:

```sh
python3 jenu.py --key clave --forwarding 80:8081 --vps 234.322.3.12
```

¡Genial, verdad? Asegúrate de que el puerto 8081 esté accesible en tu VPS.

### Listar Túneles

Para ver los túneles activos en tu máquina local, ejecuta:

```sh
python3 jenu.py --list
```

Esto mostrará algo como:

```sh
root        1577  0.1  0.1  16164  9744 pts/1    S    15:18   0:13 ssh -i clave -N -R 222:localhost:22 root@34.16.227.83
```

El primer número (`1577`) es el PID, el ID del proceso que puedes usar para detener el túnel.

### Parar el Túnel

Para detener un túnel, necesitas el PID. Puedes hacerlo manualmente:

```sh
kill 1577
```

O usando `jenu.py`:

```sh
python3 jenu.py --stop 1577
```

¡Que lo disfrutes!

## Ejemplo

Digamos que tienes un servidor HTTP en tu máquina local en el puerto 8081:

```sh
python3 -m http.server 8081
```

Ahora, en tu VPS con dirección `43.53.233.43`, tienes abierto el puerto 80 a internet. Para publicar tu servidor HTTP, ejecuta:

```sh
python3 jenu.py -k clavesshvps -f 8081:80 -v 43.53.233.43
```

Ahora, si accedes a `43.53.233.43:80` desde internet, verás el servidor que está corriendo en `localhost:8081`.

Puedes hacer esto con cualquier servicio: servidores de bases de datos, servidores SSH, HTTP, TCP, lo que quieras!