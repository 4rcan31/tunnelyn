# Tunnel SSH - Jenu

Este proyecto te permite exponer un servidor local a internet utilizando un VPS, evitando las restricciones del CGNAT de tu ISP residencial sin necesidad de contratar un internet dedicado. En lugar de gastar más de 100 dólares al mes, puedes utilizar un VPS asequible (en AWS, GCP, DigitalOcean, etc.) para redirigir el tráfico, aprovechando su dirección IP pública y transmitiendo todo el tráfico hacia tu máquina local.

## 1. Configuración del VPS

### Habilitar Redirección de Puertos

Primero, debes configurar tu VPS para permitir la redirección de puertos (port forwarding). Para ello:

1. **Instala SSH en el VPS** y modifica el archivo de configuración SSH (`/etc/ssh/sshd_config`) para aceptar conexiones por llave y permitir la redirección de puertos. Descomenta o añade las siguientes líneas:

    ```sh
    AllowTcpForwarding yes
    GatewayPorts yes
    X11Forwarding yes
    ```

2. **Automatizar la Configuración**:
    Para simplificar, puedes usar el script `ssh_vps_config/install.sh` que configurará las reglas anteriores automáticamente:

    - Darle permisos de ejecución al script:
        ```sh
        sudo chmod +x ssh_vps_config/install.sh
        ```
    - Ejecutar el script:
        ```sh
        sudo ./ssh_vps_config/install.sh
        ```

3. **Revisar el Firewall**: No olvides abrir los puertos necesarios en el firewall del VPS para que las conexiones puedan ser aceptadas.

---

## 2. Configuración del Servidor Local

Ahora que el VPS está listo, puedes usar el programa CLI `jenu.py` para gestionar la apertura y cierre de puertos en tu servidor local.

### 2.1 Confiar en el Host (Primera Conexión)

La primera vez que te conectes por SSH, tu máquina local pedirá confirmar la confianza en el VPS. Para ello:

1. Ejecuta el siguiente comando para verificar la confianza:
    ```sh
    python3 jenu.py -k <clave> -v <ip_del_vps> --verify
    ```

2. Si el comando falla, realiza una conexión manual una vez:
    ```sh
    ssh -i <clave> root@<ip_del_vps>
    ```

---

## 3. Comandos para Gestionar Túneles SSH

### 3.1 Abrir un Túnel de Puertos

Para abrir un túnel y redirigir tráfico desde tu VPS hacia tu servidor local, ejecuta:

```sh
python3 jenu.py -k <clave> -f <puerto_local>:<puerto_vps> -v <ip_del_vps>
```

- Ejemplo: Redirigir el puerto 80 local al puerto 8081 del VPS:
    ```sh
    python3 jenu.py -k clave -f 80:8081 -v 234.322.3.12
    ```

Puedes usar el formato extendido del comando si lo prefieres:
```sh
python3 jenu.py --key <clave> --forwarding <puerto_local>:<puerto_vps> --vps <ip_del_vps>
```

### 3.2 Listar Túneles Activos

Para ver una lista de los túneles SSH activos, ejecuta:

```sh
python3 jenu.py --list
```

Esto mostrará el PID (ID de proceso) del túnel, por ejemplo:
```sh
root 1577  0.1  0.1  16164  9744 pts/1    S  15:18   0:13 ssh -i clave -N -R 222:localhost:22 root@34.16.227.83
```
El primer número (`1577`) es el PID del túnel.

### 3.3 Detener un Túnel

Para detener un túnel, usa el PID listado anteriormente:

- Manualmente:
    ```sh
    kill <pid>
    ```
- Usando `jenu.py`:
    ```sh
    python3 jenu.py --stop <pid>
    ```

---

## 4. Uso de Configuraciones JSON

Puedes utilizar un archivo JSON para definir múltiples configuraciones de túneles y gestionarlos fácilmente.

### 4.1 Archivo de Configuración

El archivo de configuración debe tener la siguiente estructura:

```json
[
    {
        "key": "ruta_a_la_clave_privada",
        "forwarding": "3000:51829",
        "vps": "157.245.88.73"
    },
    {
        "key": "ruta_a_la_clave_privada",
        "forwarding": "8081:51828",
        "vps": "157.245.88.78",
        "name": "backend-cbii"
    }
]
```

- `key`, `forwarding`, y `vps` son campos obligatorios.
- `name` es un campo opcional que te permite asignar un nombre al túnel.

### 4.2 Abrir y Cerrar Túneles con JSON

#### Abrir un Túnel Usando el Archivo de Configuración

Puedes abrir un túnel especificando el `name` definido en el archivo de configuración:

```sh
python3 jenu.py --up <name> --config <ruta_del_json>
```

O usando los valores de `forwarding` y `vps`:

```sh
python3 jenu.py --up <forwarding> --vps <ip_del_vps> --config <ruta_del_json>
```

#### Detener un Túnel Usando el Archivo de Configuración

Para detener un túnel, utiliza uno de los siguientes métodos:

- Por `name`:
    ```sh
    python3 jenu.py --stop <name> --config <ruta_del_json>
    ```
- Por `forwarding` y `vps`:
    ```sh
    python3 jenu.py --stop <forwarding> -v <ip_del_vps> --config <ruta_del_json>
    ```

### 4.3 Reiniciar Túneles

Para reiniciar todos los túneles definidos en el archivo de configuración, ejecuta:

```sh
python3 jenu.py --restart --config <ruta_del_json>
```

Si no pasas el archivo de configuración, `jenu.py` reiniciará los túneles activos.

---

## 5. Ejemplo Completo de Uso

Supongamos que tienes un servidor HTTP corriendo en tu máquina local en el puerto `8081`:

```sh
python3 -m http.server 8081
```

Para exponer este servidor a internet usando un VPS con dirección `43.53.233.43` y puerto público `80`, ejecuta:

```sh
python3 jenu.py -k <clave_ssh> -f 8081:80 -v 43.53.233.43
```

Ahora cualquier persona que acceda a `http://43.53.233.43:80` verá tu servidor local que está corriendo en `localhost:8081`.