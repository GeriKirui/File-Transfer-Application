import sys
import socket
from ServerPI import ServerPI

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind(("127.0.0.1", 21))

# Let Server listen continuously
s.listen()

# Accept connection request
conn, addr = s.accept()

server = ServerPI("Server", "127.0.0.1", 21, conn, addr)
server.start()

while True:
	# Allow Server to listen continuously
	s.listen()
	# Accept the request to connect
	conn, addr = s.accept()
	# Create a thread to receive data from clients
	server = ServerPI("Server", "127.0.0.1", 21, conn, addr)
	# start thread
	server.start()