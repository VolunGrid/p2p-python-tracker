import socket
import json

# Configuración de conexión
HOST = '0.0.0.0' 
PORT = 6881

def iniciar_tracker():
    # 1. Crear el socket (AF_INET = IPv4, SOCK_STREAM = protocolo TCP)
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as servidor:
        
        # 2. Enlazar el socket a nuestra dirección y puerto
        servidor.bind((HOST, PORT))
        
        # 3. Poner el servidor en modo "escucha"
        servidor.listen()
        print(f"🚀 Tracker P2P iniciado. Escuchando en {HOST}:{PORT}...")

        # El ciclo infinito mantiene el servidor vivo esperando clientes
        while True:
            # 4. Cuando la app se conecta, aceptamos la llamada
            conexion, direccion = servidor.accept()
            
            with conexion:
                print(f"\n🔗 Nueva conexión detectada desde: {direccion}")
                
                # 5. Recibir los datos (Leemos hasta 1024 bytes)
                datos_recibidos = conexion.recv(1024)
                if not datos_recibidos:
                    continue
                
                # 6. Intentar decodificar el mensaje como JSON
                try:
                    mensaje_cliente = json.loads(datos_recibidos.decode('utf-8'))
                    print(f"📥 App dice: {mensaje_cliente}")
                    
                    # 7. Si es el saludo inicial, respondemos usando el Contrato
                    if mensaje_cliente.get("action") == "handshake":
                        respuesta = {
                            "status": "success",
                            "message": "Bienvenido al enjambre",
                            "tracker_version": "1.0.0"
                        }
                        
                        # Convertimos el diccionario a JSON, luego a bytes, y lo enviamos
                        conexion.sendall(json.dumps(respuesta).encode('utf-8'))
                        print("📤 Respuesta enviada a la app con éxito.")
                        
                except json.JSONDecodeError:
                    print("❌ Error: Se recibió texto, pero no era un formato JSON válido.")

if __name__ == "__main__":
    iniciar_tracker()