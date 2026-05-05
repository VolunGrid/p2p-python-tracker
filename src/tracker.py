import socket
import json
import threading # <-- 1. AÑADIDO PARA MULTITHREADING

# Configuración de conexión
HOST = '0.0.0.0' 
PORT = 6881

# 2. NUESTRO DIRECTORIO EN MEMORIA (Tarjeta #9)
directorio_pares = {}

# 3. NUEVA FUNCIÓN PARA MANEJAR CADA CELULAR POR SEPARADO (Tarjeta #8)
def manejar_cliente(conexion, direccion):
    print(f"\n🔗 Nueva conexión detectada desde: {direccion}")
    with conexion:
        try:
            # Recibir los datos (Leemos hasta 1024 bytes)
            datos_recibidos = conexion.recv(1024)
            if datos_recibidos:
                # Intentar decodificar el mensaje como JSON
                mensaje_cliente = json.loads(datos_recibidos.decode('utf-8'))
                print(f"📥 App dice: {mensaje_cliente}")
                
                # Si es el saludo inicial, respondemos y lo REGISTRAMOS
                if mensaje_cliente.get("action") == "handshake":
                    
                    # Extraemos los datos del JSON que mandó la app
                    client_id = mensaje_cliente.get("client_id")
                    
                    # 🚀 TRUCO P2P: Ignoramos el JSON y sacamos la IP real del socket
                    ip_local = direccion[0] 
                    
                    puerto_escucha = mensaje_cliente.get("puerto_escucha")
                    
                    # Lo guardamos en nuestro directorio si mandó su ID
                    if client_id:
                        directorio_pares[client_id] = {
                            "ip": ip_local,
                            "puerto": puerto_escucha
                        }
                        print(f"📗 ¡Nuevo par registrado! Directorio actual:\n {directorio_pares}")

                    # Preparamos la respuesta para la app
                    respuesta = {
                        "status": "success",
                        "message": "Bienvenido al enjambre",
                        "tracker_version": "1.0.0"
                    }
                    
                    # Convertimos a JSON, luego a bytes, y lo enviamos
                    conexion.sendall(json.dumps(respuesta).encode('utf-8'))
                    print("📤 Respuesta enviada a la app con éxito.")

                    # --- NUEVA ACCIÓN: get_peers (Tarjeta #10) ---
                elif mensaje_cliente.get("action") == "get_peers":
                    print(f"🔍 El celular {direccion[0]} solicitó el directorio de pares.")
                    respuesta = {
                        "status": "success",
                        "peers": directorio_pares 
                    }
                    conexion.sendall(json.dumps(respuesta).encode('utf-8'))
                    print("📤 Directorio enviado con éxito.")

                # --- NUEVA ACCIÓN: disconnect (Tarjeta #11) ---
                elif mensaje_cliente.get("action") == "disconnect":
                    client_id = mensaje_cliente.get("client_id")
                    
                    # Si el celular está en el diccionario, lo borramos con 'del'
                    if client_id and client_id in directorio_pares:
                        del directorio_pares[client_id]
                        print(f"🧹 Limpieza: {client_id} se fue. Directorio actualizado: {directorio_pares}")
                    
        # --- MEJORA DE EXCEPCIONES (Tarjeta #11) ---
        # Esto evita que el servidor crashee si a un celular se le va el WiFi
        except ConnectionResetError:
            print(f"⚠️ El dispositivo {direccion[0]} perdió la conexión repentinamente.")
        except json.JSONDecodeError:
            print("❌ Error: Se recibió texto, pero no era un formato JSON válido.")
        except Exception as e:
            print(f"❌ Error inesperado con {direccion}: {e}")

def iniciar_tracker():
    # Crear el socket (AF_INET = IPv4, SOCK_STREAM = protocolo TCP)
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as servidor:
        
        # Enlazar el socket a nuestra dirección y puerto
        servidor.bind((HOST, PORT))
        
        # Poner el servidor en modo "escucha"
        servidor.listen()
        print(f"🚀 Tracker P2P iniciado. Escuchando en {HOST}:{PORT}...")

        # El ciclo infinito mantiene el servidor vivo esperando clientes
        while True:
            # 4. Cuando la app se conecta, aceptamos la llamada
            conexion, direccion = servidor.accept()
            
            # 5. EN VEZ DE ATENDERLO DIRECTO, ABRIMOS UN "HILO" NUEVO (Multithreading)
            # Así el ciclo vuelve a girar inmediatamente para esperar a otro celular
            hilo = threading.Thread(target=manejar_cliente, args=(conexion, direccion))
            hilo.start()

if __name__ == "__main__":
    iniciar_tracker()