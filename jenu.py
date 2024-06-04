import argparse
import subprocess

def open_port(key, forwarding, vps):
    local_port, remote_port = forwarding.split(':')
    existing_tunnel_pids = find_existing_tunnels(key, forwarding, vps)
    if existing_tunnel_pids:
        print("Found existing tunnel(s) with the same configuration. Stopping before opening a new one...")
        for pid, config in existing_tunnel_pids:
            print(f"Stopping existing tunnel with PID {pid}: {config}")
            stop_tunnel(pid)
    else:
        print("No existing tunnel found with the same configuration. Opening a new one...")
    command = f'ssh -i {key} -N -R {remote_port}:localhost:{local_port} root@{vps}'
    subprocess.Popen(command, shell=True)

def find_existing_tunnels(key, forwarding, vps):
    local_port, remote_port = forwarding.split(':')
    command = f'ps aux | grep "ssh -i {key} -N -R {remote_port}:localhost:{local_port} root@{vps}" | grep -v grep'
    try:
        output = subprocess.check_output(command, shell=True).decode("utf-8")
        existing_tunnel_pids = []
        for line in output.split("\n"):
            parts = line.split()
            if len(parts) >= 2:
                pid = parts[1]
                config = f"SSH key: {key}, Forwarding: {forwarding}, VPS: {vps}"
                existing_tunnel_pids.append((pid, config))
        return existing_tunnel_pids
    except subprocess.CalledProcessError:
        return []

def list_tunnels(all=False):
    print("Active SSH tunnels:")
    if all:
        subprocess.run("ps aux | grep ssh", shell=True)
    else:
        ssh_processes = subprocess.check_output("ps aux | grep ssh", shell=True).decode("utf-8").split("\n")
        for process in ssh_processes:
            if "ssh" in process and "-N -R" in process:
                print(process)

def stop_tunnel(pid):
    subprocess.run(["kill", str(pid)])
    print(f"Stopped tunnel with PID {pid}")

def verify_host(key, forwarding, vps):
    print("Verifying host authenticity...")
    command = f'ssh -o StrictHostKeyChecking=yes -i {key} root@{vps} "exit"'
    subprocess.run(command, shell=True)

def main():
    parser = argparse.ArgumentParser(description='Open and manage SSH tunnels')
    parser.add_argument('-k', '--key', type=str, help='Path to SSH private key (required)')
    parser.add_argument('-f', '--forwarding', type=str, help='Forwarding configuration (e.g., 80:8081) (required)')
    parser.add_argument('-v', '--vps', type=str, help='IP address or hostname of the VPS (required)')
    parser.add_argument('--stop', type=int, metavar='PID', help='Stop tunnel by PID')
    parser.add_argument('--list', action='store_true', help='List active tunnels')
    parser.add_argument('--all', action='store_true', help='List all SSH processes, not just SSH tunnels')
    parser.add_argument('--verify', action='store_true', help='Verify host authenticity and add to known hosts')
    args = parser.parse_args()

    if args.list:
        list_tunnels(all=args.all)
    elif args.stop:
        stop_tunnel(args.stop)
    elif args.verify:
        verify_host(args.key, args.forwarding, args.vps)
    elif args.key and args.forwarding and args.vps:
        open_port(args.key, args.forwarding, args.vps)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
