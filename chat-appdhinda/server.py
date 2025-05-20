import socket
import threading
import cv2
import pickle
import struct
import numpy as np



HOST = '192.168.245.63'
PORT = 55555

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((HOST, PORT))
server.listen()

clients = []
nicknames = []

def broadcast(message):
    for client in clients:
        client.send(message)

def handle(client):
    data = b""
    payload_size = struct.calcsize("Q")
    while True:
        try:
            while len(data) < payload_size:
                packet = client.recv(4*1024)  # 4KB chunks
                if not packet:
                    return
                data += packet

            packed_msg_size = data[:payload_size]
            data = data[payload_size:]
            msg_size = struct.unpack("Q", packed_msg_size)[0]

            while len(data) < msg_size:
                data += client.recv(4*1024)

            frame_data = data[:msg_size]
            data = data[msg_size:]

            frame = pickle.loads(frame_data)
            cv2.imshow(f"Video dari client", frame)
            if cv2.waitKey(1) == ord('q'):
                break
        except Exception as e:
            print(f"Client error: {e}")
            break
    cv2.destroyAllWindows()


def receive():
    print(f"Server berjalan di {HOST}:{PORT}")
    while True:
        client, address = server.accept()
        print(f"Terhubung dengan {address}")

        client.send('NICK'.encode())
        nickname = client.recv(1024).decode()
        nicknames.append(nickname)
        clients.append(client)

        print(f"Nickname: {nickname}")
        broadcast(f'{nickname} joined the chat!'.encode())
        client.send('Terhubung ke server!'.encode())

        thread = threading.Thread(target=handle, args=(client,))
        thread.start()
        

receive()
