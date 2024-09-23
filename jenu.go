package main

import (
	"encoding/json"
	"fmt"
	"log"
	"os"
	"os/exec"
	"strings"
)

type TunnelConfig struct {
	Key        string `json:"key"`
	VPS        string `json:"vps"`
	LocalPort  string `json:"local_port"`
	RemotePort string `json:"remote_port"`
}

func main() {
	if len(os.Args) < 3 {
		log.Fatalf("Debe proporcionar la ruta al archivo de configuración JSON y la acción (reiniciar/desconectar/listar) como argumentos")
	}

	filePath := os.Args[1]
	action := os.Args[2]

	// Leer archivo JSON con la configuración de los túneles
	tunnels, err := readTunnelConfig(filePath)
	if err != nil {
		log.Fatalf("Error leyendo archivo de configuración: %v", err)
	}

	// Procesar acción sobre cada túnel
	for _, tunnel := range tunnels {
		fmt.Printf("Procesando túnel: VPS: %s, LocalPort: %s, RemotePort: %s\n", tunnel.VPS, tunnel.LocalPort, tunnel.RemotePort)

		switch action {
		case "reiniciar":
			restartTunnel(tunnel)
		case "desconectar":
			disconnectTunnel(tunnel)
		case "listar":
			ListarTuneles()
		default:
			fmt.Println("Acción no reconocida. Use 'reiniciar' o 'desconectar'.")
		}
	}
}

// Leer el archivo JSON de configuración
func readTunnelConfig(filePath string) ([]TunnelConfig, error) {
	file, err := os.Open(filePath)
	if err != nil {
		return nil, err
	}
	defer file.Close()

	var tunnels []TunnelConfig
	err = json.NewDecoder(file).Decode(&tunnels)
	if err != nil {
		return nil, err
	}

	return tunnels, nil
}

// Verificar si ya hay un túnel SSH activo con el puerto remoto
func isTunnelActive(tunnel TunnelConfig) bool {
	cmd := exec.Command("bash", "-c", fmt.Sprintf("ps aux | grep 'ssh' | grep '%s' | grep -v grep", tunnel.RemotePort))
	output, err := cmd.Output()

	if err != nil {
		fmt.Println("Error ejecutando el comando para buscar túneles existentes:", err)
		return false
	}

	return strings.TrimSpace(string(output)) != ""
}

// Abrir un nuevo túnel SSH
func openTunnel(tunnel TunnelConfig) {
	cmd := exec.Command("ssh", "-i", tunnel.Key, "-N", "-R", fmt.Sprintf("%s:localhost:%s", tunnel.RemotePort, tunnel.LocalPort), fmt.Sprintf("root@%s", tunnel.VPS))
	err := cmd.Start()

	if err != nil {
		fmt.Printf("Error al abrir el túnel: %v\n", err)
		return
	}

	fmt.Printf("Túnel abierto exitosamente en el puerto remoto %s.\n", tunnel.RemotePort)
}

// Cerrar túnel SSH activo
func closeTunnel(tunnel TunnelConfig) bool {
	cmd := exec.Command("bash", "-c", fmt.Sprintf("ps aux | grep 'ssh' | grep '%s' | grep '%s' | grep -v grep | awk '{print $2}'", tunnel.VPS, tunnel.RemotePort))
	output, err := cmd.Output()

	if err != nil {
		fmt.Printf("Error buscando túneles existentes: %v\n", err)
		return false
	}

	pid := strings.TrimSpace(string(output))
	if pid != "" {
		// Matar el proceso SSH
		killCmd := exec.Command("kill", pid)
		err := killCmd.Run()
		if err != nil {
			fmt.Printf("Error al cerrar el túnel con PID %s: %v\n", pid, err)
			return false
		}
		fmt.Printf("Túnel con PID %s detenido exitosamente.\n", pid)
		return true
	}

	fmt.Printf("No se encontró un túnel activo para VPS: %s, RemotePort: %s\n", tunnel.VPS, tunnel.RemotePort)
	return false
}

// Reiniciar un túnel SSH
func restartTunnel(tunnel TunnelConfig) {
	if isTunnelActive(tunnel) {
		fmt.Printf("Reiniciando túnel para VPS: %s, RemotePort: %s\n", tunnel.VPS, tunnel.RemotePort)
		if closeTunnel(tunnel) {
			openTunnel(tunnel)
		}
	} else {
		fmt.Printf("No se encontró un túnel activo en el puerto remoto %s. Abriendo un nuevo túnel...\n", tunnel.RemotePort)
		openTunnel(tunnel)
	}
}

// Desconectar un túnel SSH
func disconnectTunnel(tunnel TunnelConfig) {
	fmt.Printf("Desconectando túnel para VPS: %s, RemotePort: %s\n", tunnel.VPS, tunnel.RemotePort)
	closeTunnel(tunnel)
}

func ListarTuneles() {
	fmt.Println("Túneles SSH activos:")
	command := "ps aux | grep 'ssh' | grep 'localhost' | grep -v grep"
	output, err := exec.Command("bash", "-c", command).Output()
	if err != nil {
		fmt.Printf("Error listando túneles: %v\n", err)
		return
	}
	fmt.Println(string(output))
}
