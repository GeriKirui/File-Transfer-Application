import socket
import random
import os

# This file contains the implementation of the user data transfer protocol (user DTP)

# A class that implements the user DTP
class ClientDTP():
	def __init__(self):
		# Member variables
		self.dataConnection = None
		self.dataSocket = None
		self.dataPortUpper = None
		self.dataportLower = None
		self.dataPort = None
		self.isConnectionOpen = False
		self.isConnectionPassive = True
		self.bufferSize = 1024
		self.receptionFolder = "FromServer/"
		self.sendFolder = "ToServer/"
		self.remoteList = None

# Functions for the establishment of an active data connection
# ---------------------------------------------------------------------------------
	# A function to make a port number for an active connection
	def makeActiveDataPort(self):
		# Use random numbers within a specified range
		self.dataPortUpper = str(random.randint(20,30))
		self.dataportLower = str(random.randint(0,255))
		self.dataPort = (int(self.dataPortUpper) * 256) + int(self.dataportLower) # Assign the port

	# A function to set the address of the client for an active connection
	def activeClientAddress(self,address):
		# Formatting
		address = address.split(".") # Get the numbers between the periods
		address = ",".join(address) # Separate the numbers with a comma 
		address = address + "," + self.dataPortUpper + "," + self.dataportLower # Concatenate the port number
		return address # return the address

	# A function to actively listen for a connection
	def listenActive(self,ip):
		# Set up the socket and listen for a connection
		self.makeActiveDataPort()
		self.dataSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.dataSocket.bind((ip,self.dataPort))
		self.dataSocket.listen(1)

	# A function to accept a connection from the server
	def acceptActiveConn(self):
		self.dataConnection,dataIP = self.dataSocket.accept()
		self.isConnectionOpen = True
		print("Successful active data connection\r\n")

# Functions for the establishemnt of a passive data connection
# -----------------------------------------------------------------------------------------
	# A function to extract the IP address of the server from the address
	def extractPassiveServerIP(self,address):
		ip = address[0] + "." + address[1] + "." + address[2] + "." + address[3]
		return ip

	# A function to extract the port number of the server from the address
	def extractPassiveServerPort(self,address):
		self.dataPortUpper = str(address[-2])
		self.dataportLower = str(address[-1])
		self.dataPort = (int(address[-2]) * 256) + int(address[-1])
		return self.dataPort

	# A function that returns the address in a different format
	def extractAddr(self,address):
		# Simply return the numbers in the brackets without the commas
		first = address.find("(") + 1
		second = address.find(")")
		address = address[first:second]
		address = address.split(",")
		return address

	# A function that makes the connection passive
	def makeConnPassive(self,address):
		try: # Get the IP address and port number
			extracted_address = self.extractAddr(address)
			ip = self.extractPassiveServerIP(extracted_address)
			port = self.extractPassiveServerPort(extracted_address)
			# Set up socket
			self.dataConnection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			self.dataConnection.connect((ip,port)) # Connect
			self.isConnectionOpen = True
			print("Successful passive data connection\r\n")
		except:
			print("Could not establish passive connection\r\n")
			self.closeData()

# Functions for querying the data connection
# -----------------------------------------------------------------------------------------	
	# A function that checks whether the data connection is established
	def isDataConnEstablished(self):
		return self.isConnectionOpen

	def isPassive(self):
		return self.isConnectionPassive

# Functions for managing the data connection
# ------------------------------------------------------------------------------------------
	# A function that returns the active/passive status of a connection
	def dataMode(self,mode = True):
		if mode:
			self.isConnectionPassive = True
		else:
			self.isConnectionPassive = False

	# A function that closes the data transfer protocol 
	def closeData(self):
		# If the data connection is open
		if self.isConnectionOpen and self.dataConnection != None:
			self.dataConnection.close() # Close the data connection
			self.isConnectionOpen = False # Set the flag to false
			print("Terminating data connection.\r\n") # Inform the client

# Functions for querying the file system (getters)
# -------------------------------------------------------------------------------------------
	# A function that determines whether a file exists in the file system
	def doesFileExist(self,fName):
		path = self.sendFolder + fName # concatenate the folder name to the filename
		if os.path.isfile(path):
			return True
		return False

# Functions for file transfer
# ------------------------------------------------------------------------------------------	
	# A function that recieves a file from the server
	def fromServer(self,fName):
		# Open a file
		file = open(self.receptionFolder + fName,"wb")
		# Declare a variable to receive file bytes
		data = self.dataConnection.recv(self.bufferSize)
		# Receive data
		while data: # while the file is being transferred:
			file.write(data) # write to the file
			data = self.dataConnection.recv(self.bufferSize) # receive the next data in the buffer
		file.close() # Close the file

	# A function to send a file to the server
	def toServer(self,fName):
		# Open a file
		file = open(self.sendFolder + fName,"rb")
		# Declare a variable to send file bytes
		data = file.read(self.bufferSize)

		# Send data
		while data: # while the file is being transferred:
			self.dataConnection.send(data) # Send the current data in the buffer
			data = file.read(self.bufferSize) # read the next data to the buffer
		file.close() # close the file after transfer is complete

	# A function to get the file list from the server
	def downloadRemoteList(self):
		# recieve and decode the byte version of the file
		data = self.dataConnection.recv(self.bufferSize).decode().rstrip()
		self.remoteList = []
		while data:
			info = data.split("\r")
			for item in info:
				item = item.strip().rstrip()
				self.makeList(item)
				data = self.dataConnection.recv(self.bufferSize).decode().rstrip()

	# A function that formats the server
	def makeList(self,item):
		dummy = item.split()
		fName = "".join(dummy[8:])
		fSize = str("".join(dummy[4:5])) + " Bytes"
		lastModified = "".join(dummy[5:8])
		permissions = "".join(dummy[0:1])
		dummyList = [fName, fSize, lastModified, permissions]
		dummyList = list(filter(None, dummyList))
		self.remoteList.append(dummyList)

	# A function that gets the file-list on the client side
	def getRemoteList(self):
		return self.remoteList
