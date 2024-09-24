import argparse
import json
import subprocess   
import logging
import os
import stat
import re


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def set_key_permissions(key, debug=False):
    if debug:
        logger.debug(f"Setting permissions for key: {key}")
    try:
        os.chmod(key, stat.S_IRUSR | stat.S_IWUSR)  # Permisos 600: lectura y escritura solo para el usuario
        if debug:
            logger.info(f"Permissions for key {key} set to 600 (read and write for user only).")
    except Exception as e:
        logger.error(f"Failed to set permissions for key {key}: {e}")

def open_port(key, forwarding, vps, debug=False):
    local_port, remote_port = forwarding.split(':')

    set_key_permissions(key, debug)
    if debug:
        logger.debug(f"Attempting to open port: Local port: {local_port}, Remote port: {remote_port}, VPS: {vps}")

    existing_tunnel_pids = find_existing_tunnels(key, forwarding, vps, debug)
    if existing_tunnel_pids:
        logger.info("Found existing tunnel(s) with the same configuration. Stopping before opening a new one...")
        for pid, config in existing_tunnel_pids:
            logger.info(f"Stopping existing tunnel with PID {pid}: {config}")
            stop_tunnel(pid, debug)
    else:
        logger.info("No existing tunnel found with the same configuration. Opening a new one...")

    command = f'ssh -i {key} -N -R {remote_port}:localhost:{local_port} root@{vps}'
    if debug:
        logger.debug(f"Executing command: {command}")
    subprocess.Popen(command, shell=True)

def find_existing_tunnels(key, forwarding, vps, debug=False):
    local_port, remote_port = forwarding.split(':')
    command = f'ps aux | grep "ssh -i {key} -N -R {remote_port}:localhost:{local_port} root@{vps}" | grep -v grep'
    if debug:
        logger.debug(f"Searching for existing tunnels with command: {command}")

    try:
        output = subprocess.check_output(command, shell=True).decode("utf-8")
        existing_tunnel_pids = []
        for line in output.split("\n"):
            parts = line.split()
            if len(parts) >= 2:
                pid = parts[1]
                config = f"SSH key: {key}, Forwarding: {forwarding}, VPS: {vps}"
                existing_tunnel_pids.append((pid, config))
                if debug:
                    logger.debug(f"Found existing tunnel: PID {pid}, Config: {config}")
        return existing_tunnel_pids
    except subprocess.CalledProcessError as e:
        if debug:
            logger.error(f"Error finding existing tunnels: {e}")
        return []

def list_tunnels(all=False, debug=False):
    logger.info("Active SSH tunnels:")
    if all:
        subprocess.run("ps aux | grep ssh", shell=True)
    else:
        ssh_processes = subprocess.check_output("ps aux | grep ssh", shell=True).decode("utf-8").split("\n")
        for process in ssh_processes:
            if "ssh" in process and "-N -R" in process:
                logger.info(process)
                if debug:
                    logger.debug(f"Active tunnel process: {process}")

def stop_tunnel(pid, debug=False):
    subprocess.run(["kill", str(pid)])
    logger.info(f"Stopped tunnel with PID {pid}")
    if debug:
        logger.debug(f"Sent kill signal to PID: {pid}")

def verify_host(key, vps, debug=False):
    logger.info("Verifying host authenticity...")
    command = f'ssh -o StrictHostKeyChecking=yes -i {key} root@{vps} "exit"'
    if debug:
        logger.debug(f"Executing command to verify host: {command}")
    subprocess.run(command, shell=True)

def load_config(file_path, debug=False):
    if debug:
        logger.debug(f"Loading configuration from {file_path}")
    with open(file_path, 'r') as file:
        return json.load(file)

def stop_tunnel_by_forwarding(forwarding, vps, debug=False):
    logger.info(f"Stopping tunnel with forwarding: {forwarding}")
    
    try:
        local_port, remote_port = forwarding.split(':')
        logger.debug(f"Parsed forwarding: local_port={local_port}, remote_port={remote_port}")

        # Ejecutar el comando para listar procesos SSH
        output = subprocess.check_output("ps aux | grep ssh", shell=True).decode("utf-8").split("\n")
        logger.debug(f"SSH processes: {output}")

        found = False
        pattern = re.compile(r"-N -R\s+{}:localhost:{}\s+root@{}".format(remote_port, local_port, re.escape(vps)))


        # Revisar cada proceso en la salida para encontrar el túnel correspondiente
        for process in output:
            if pattern.search(process):
                parts = process.split()

                pid = parts[1]  # El segundo elemento debería ser el PID
                logger.info(f"Stopping tunnel with forwarding {forwarding} and PID {pid}")
                # Enviar señal de terminación al proceso
                subprocess.run(["kill", str(pid)])
                logger.info(f"Stopped tunnel with PID {pid}")
                found = True
                break 
        
        if not found:
            logger.info(f"No tunnel found for forwarding {forwarding}.")

    except subprocess.CalledProcessError as e:
        if debug:
            logger.error(f"Error stopping tunnel: {e}")
        else:
            logger.error("Error stopping tunnel.")



def find_tunnel_by_name(name, config, debug=False):
    for entry in config:
        if entry.get('name') == name:
            return entry
    return None

def main():
    parser = argparse.ArgumentParser(description='Open and manage SSH tunnels')
    parser.add_argument('-k', '--key', type=str, help='Path to SSH private key (required)')
    parser.add_argument('-f', '--forwarding', type=str, help='Forwarding configuration (e.g., 80:8081) (required)')
    parser.add_argument('-v', '--vps', type=str, help='IP address or hostname of the VPS (required)')
    parser.add_argument('--config', type=str, help='Path to the JSON configuration file')
    parser.add_argument('--stop', nargs='?', const=True, help='Stop a tunnel by name or by forwarding configuration')
    parser.add_argument('--pid', type=int, metavar='PID', help='PID of the tunnel to stop (if stopping by PID)')
    parser.add_argument('--list', action='store_true', help='List active tunnels')
    parser.add_argument('--all', action='store_true', help='List all SSH processes, not just SSH tunnels')
    parser.add_argument('--verify', action='store_true', help='Verify host authenticity and add to known hosts')
    parser.add_argument('--debug', action='store_true', help='Enable debug output')
    parser.add_argument('--up', type=str, help='Start a tunnel by name or forwarding configuration')
    parser.add_argument('--stop-name', type=str, help='Stop a tunnel by name')

    args = parser.parse_args()

    if args.debug:
        logger.setLevel(logging.DEBUG)

    # Cargar y ejecutar configuraciones desde el archivo JSON si se especifica
    if args.config:
        config = load_config(args.config, args.debug)
        logger.info(f"Loaded configurations: {config}")

        # Comando --up para iniciar un túnel específico
        if args.up:
            if args.key and args.forwarding and args.vps:
                open_port(args.key, args.forwarding, args.vps, args.debug)

            elif re.match(r'^\d+:\d+$', args.up):  # Si es un forwarding
                forwarding = args.up
                found = False
                for comando in config:
                    if comando['forwarding'] == forwarding:
                        open_port(comando['key'], comando['forwarding'], comando['vps'], args.debug)
                        found = True
                        break
                if not found:
                    logger.error(f"No configuration found for forwarding: {forwarding}")
            else:  # Si es un nombre de túnel
                comando = find_tunnel_by_name(args.up, config, args.debug)
                if comando:
                    open_port(comando['key'], comando['forwarding'], comando['vps'], args.debug)
                else:
                    logger.error(f"No configuration found for name: {args.up}")

        # Comando --stop para detener un túnel específico
        elif args.stop:
            if args.pid:
                stop_tunnel(args.pid, debug=args.debug)
            
            elif args.forwarding and args.vps:
                stop_tunnel_by_forwarding(args.forwarding, args.vps, debug=args.debug)

            elif re.match(r'^\d+:\d+$', args.stop):  # Si es un forwarding para --stop
                forwarding = args.stop
                found = False
                for comando in config:
                    if comando['forwarding'] == forwarding:
                        stop_tunnel_by_forwarding(comando['forwarding'], comando['vps'], args.debug)
                        found = True
                        break
                if not found:
                    logger.error(f"No configuration found for forwarding: {forwarding}")
            else:  # Si es un nombre de túnel para --stop
                comando = find_tunnel_by_name(args.stop, config, args.debug)
                if comando:
                    stop_tunnel_by_forwarding(comando['forwarding'], comando['vps'], args.debug)
                else:
                    logger.error(f"No configuration found for name: {args.stop}")
        
        else:
            for comando in config:
                open_port(comando['key'], comando['forwarding'], comando['vps'], args.debug)

    # Listar túneles activos si se usa el argumento --list
    elif args.list:
        list_tunnels(all=args.all, debug=args.debug)

    # Verificar autenticidad del host con --verify
    elif args.verify:
        if args.key and args.vps:
            verify_host(args.key, args.vps, debug=args.debug)
        else:
            logger.error("To verify host, both --key and --vps must be provided.")

    # Abrir un túnel directamente si se proporcionan key, forwarding, y vps
    elif args.key and args.forwarding and args.vps:
        open_port(args.key, args.forwarding, args.vps, debug=args.debug)

    # Si no se proporcionan argumentos, mostrar ayuda
    else:
        parser.print_help()

if __name__ == "__main__":
    main()