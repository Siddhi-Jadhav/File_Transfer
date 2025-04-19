# server.py

import socket
import os
import tqdm

# Configuration
SERVER_HOST = '0.0.0.0'      # Accept connection from any IP
SERVER_PORT = 5001           # Port to listen on
BUFFER_SIZE = 4096           # Chunk size
SEPARATOR = "<SEPARATOR>"    # Used to separate filename and filesize

# Create socket and listen
server_socket = socket.socket()
server_socket.bind((SERVER_HOST, SERVER_PORT))
server_socket.listen(5)
print(f"[*] Listening on {SERVER_HOST}:{SERVER_PORT}")

# Accept client connection
client_socket, address = server_socket.accept()
print(f"[+] {address} connected.")

# Receive file info
received = client_socket.recv(BUFFER_SIZE).decode()
filename, filesize = received.split(SEPARATOR)
filename = os.path.basename(filename)
filesize = int(filesize)

# Receive the file and save it
with open("received_" + filename, "wb") as f, tqdm.tqdm(
    total=filesize, unit="B", unit_scale=True, desc=f"Receiving {filename}"
) as progress:
    while True:
        bytes_read = client_socket.recv(BUFFER_SIZE)
        if not bytes_read:
            break
        f.write(bytes_read)
        progress.update(len(bytes_read))

client_socket.close()
server_socket.close()
print(f"[✓] File received and saved as 'received_{filename}'")
