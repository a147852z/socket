import time
import socket
import threading
import json

clients = {}
addresses = {}

def handle_client(client_socket):
    while True:
        try:
            message = client_socket.recv(4096).decode('utf-8')
            if message:
                json_data = json.loads(message)
                # print(f"Received JSON from {client_socket.getpeername()}: {json_data}")
                target = json_data.get("target")
                if target and target in clients:
                    send_json_to_client(clients[target], json_data)
                # else:
                #     broadcast(message, client_socket)
            else:
                remove(client_socket)
                break
        except (ConnectionResetError, ConnectionAbortedError, socket.error) as e:
            print(f"Error: {e}")
            remove(client_socket)
            break

def broadcast(message, connection):
    for client in clients.values():
        if client != connection:
            try:
                client.send(message.encode('utf-8'))
            except Exception as e:
                print(f"Error broadcasting: {e}")
                remove(client)

def remove(connection):
    for name, client in list(clients.items()):
        if client == connection:
            print(f"Removing client {name} {client.getpeername()}")
            del clients[name]
            connection.close()
            break

def send_json_to_client(client_socket, json_data):
    try:
        message = json.dumps(json_data)
        client_socket.send(message.encode('utf-8'))
        print(f"Sent JSON to {client_socket.getpeername()}")
    except Exception as e:
        print(f"Error sending JSON: {e}")

def server_program(host, port):
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((host, port))
    server_socket.listen(5)
    print(f'Socket伺服器已啟動 IP:{host}, Port:{port}')

    while True:
        client_socket, client_address = server_socket.accept()
        name = client_socket.recv(1024).decode('utf-8')
        clients[name] = client_socket
        addresses[client_socket] = name
        print(f"Connection from {client_address} as {name}")

        thread = threading.Thread(target=handle_client, args=(client_socket,))
        thread.start()

def send_json_to_target(target_name, json_data):
    if target_name in clients:
        try:
            send_json_to_client(clients[target_name], json_data)
        except Exception as e:
            print(f"Error sending JSON data: {e}")
    else:
        print(f"Client {target_name} not connected")

if __name__ == "__main__":
    host = "192.168.178.151"
    port = 12345
    server_thread = threading.Thread(target=server_program, args=(host, port))
    server_thread.start()

    # 示例：手動輸入 JSON 數據並發送到指定客戶端
    time.sleep(1)
    while True:
        target_name = input("Enter target client name: ")
        with open("datatest.json", "r", encoding='utf-8') as log_file:
            log_data = json.load(log_file)
        send_json_to_target(target_name, log_data)
