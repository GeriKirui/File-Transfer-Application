import socket
from ClientDTP import ClientDTP

# This file contains the implementation of the user protocol interpreter (user PI)

# A class that implements the user PI
class ClientPI():
	def __init__(self,serverIP,cmdPort):
		# member variables
		self.clientDTP = ClientDTP()
		self.username = None
		self.serverIP = serverIP
		self.clientIP = "127.0.0.1"
		self.commandSocket = None
		self.cmdPort = int(cmdPort)
		self.commandIsActive = False
		self.isUserValid = False

# Private Functions for the sending and reception of commands
# ----------------------------------------------------------------------------------
	# A function that receives a command from the server
	def receiveCommand(self):
		reply = self.commandSocket.recv(1024).decode() # receive the reply in byte form and decode
		print(reply) # print the reply
		return reply

	# A function to send a command to the server
	def sendCommand(self,command, partial = True):
		if self.isCommandActive(): # Check if the command connection is open
			print(command)
			self.commandSocket.send(command.encode()) # If open, send the command
			reply = self.receiveCommand() 
			if partial:
				reply = reply[:3].strip()
			return reply
		else: # If the control connection is not open, inform the client
			print("Control connection inactive.\r\n")
			return "000"

# Private Functions for handling connections
# ------------------------------------------------------------------------------------
	# A function to select active transmission mode
	def activeMode(self):
		if not self.clientDTP.isDataConnEstablished(): # If the data connection has not been established
			self.clientDTP.listenActive(self.clientIP) # actively listen for a connection request
			reply = self.sendCommand("PORT " + 
			self.clientDTP.activeClientAddress(self.clientIP) + "\r\n") # use the port command
			if reply == "225": # If the reply is positive
				self.clientDTP.acceptActiveConn() # accept the connection request
			else:
				pass # Stop listening

	# A function to select passive transmission mode
	def passiveMode(self):
		if not self.clientDTP.isDataConnEstablished(): # if the data connection has not bee established
			reply = self.sendCommand("PASV\r\n",False) # send the PASV command to the server
			if reply[:3] == "227": # if the reply is positive:
				self.clientDTP.makeConnPassive(reply) # make the connection passive
			else:
				pass

	# A function that specifies whether the data connection is active or passive
	def dataConnection(self):
		if self.clientDTP.isPassive(): # If the connection is passive, select pasive mode
			self.passiveMode()
		else: #Otherwise, select active mode
			self.activeMode()

	# A function to check whether the command is active
	def isCommandActive(self):
		if self.commandIsActive: # If the command is active:
			return True # Confirm that it is active
		else: # Otherwise
			# Inform the client that it is not active
			print("Control connection inactive.\r\n")
			return False

# Private Functions for handling the login feature 
# ------------------------------------------------------------------------------------------
	# A function that determines whether the password is valid
	def isKeyValid(self,key):
		# Query the server on whether the password matches the user trying to login
		reply = self.sendCommand("PASS " + key + "\r\n")
		if reply == "230": # If the reply is 230, the password is valid
			return True
		else:
			return False # Otherwise, it is invalid

# Public Functions for handling connections (setters)
# -------------------------------------------------------------------------------------------
	# A function that opens a connection
	def openConn(self):
		try: # set up the socket
			self.commandSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			self.commandSocket.connect((self.serverIP,self.cmdPort)) # Attempt a connection
			reply = self.receiveCommand()
			if reply[:3] == "220": # If the server reply is positive:
				self.commandIsActive = True # Set the flags accordingly
			else:
				self.commandIsActive = False
		except:
			print("Unable to establish control connection\r\n")

	# A function to set the transfer mode
	def dataMode(self,mode):
		# if the mode is active, the flag is set to false in the ClientDTP
		if mode == "active":
			self.clientDTP.dataMode(False)
			print("Now transferring in active mode\r\n")
		elif mode == "passive": # Otherwise, it is set to true
			self.clientDTP.dataMode(True)
			print("Now transfering in passive mode\r\n")
		else:
			print("Invalid mode")

	# A function  to logout
	def exit(self):
		self.sendCommand("QUIT\r\n") # Send the QUIT command to the server
		self.commandSocket.close() # Close the control connection
		self.clientDTP.closeData() # Close the data connection
		self.commandIsActive = False # Set the command active flag to false
		self.isUserValid = False # Set the user active flag to false

# Public functions for querying connections (getters)
# --------------------------------------------------------------------------------------
	# A funtion to inform the user of the mode of server operation
	def getMode(self):
		# Inform the user of whether the mode is active or passive
		if self.clientDTP.isPassive():
			print("Passive mode\r\n")
		else:
			print("Active mode\r\n")

	# A function to check if the connection to the server is still active
	def ping(self):
		self.sendCommand("NOOP\r\n")

# Private functions for handling login
# ---------------------------------------------------------------------------------------
	# A function in the UI for the user to login
	def login(self,username):
		# If the user has not yet logged on before:
		if not self.isUserValid:
			reply = self.sendCommand("USER " + username + "\r\n") # Send the FTP command USER
			if reply == "331": # If the user is recognised by the server:
				self.username = username # Assign the current user
				key = input("user_input> ")
				if self.isKeyValid(key):
					self.isUserValid = True # If the password is correct, the login is successful
			else: # Otherwise, the login is unsuccessful 
				self.username = None
				self.isUserValid = False
		else: # Otherwise, the user has already logged in
			print("User has already logged in.\r\n") 

# Public functions for handling files
# -----------------------------------------------------------------------------------------
	# A function that updates the list in the server 
	def updateRemoteDirectoryList(self):
		self.dataConnection()
		if self.clientDTP.isDataConnEstablished():
			reply = self.sendCommand("LIST\r\n")
			if reply == "125":
				self.clientDTP.downloadRemoteList()
				self.receiveCommand()
		self.clientDTP.closeData()

	# A function that gets the list from the remote server
	def getRemoteDirectoryList(self):
		return self.clientDTP.getRemoteList()
	
	# A function that deletes a file in the server
	def delete(self, file):
		self.sendCommand("DELE " + file + "\r\n")
	
	# A function that retrieves a file from the server
	def download(self,fName):
		self.dataConnection() # Specify whether data connection is in active or passive mode
		# Start download process
		if self.clientDTP.isDataConnEstablished(): # If the data connection is established:
			reply = self.sendCommand("RETR " + fName + "\r\n") # Send FTP command
			if reply == "125": # Inform client of successful download
				self.clientDTP.fromServer(fName) # receive the file
				self.clientDTP.closeData() # close the data connection
				self.receiveCommand() # receive the relevant reply from the server

	# A function that sends a file to the server
	def upload(self,fName):
		# If the file does not exist, inform the user
		if not self.clientDTP.doesFileExist(fName):
			print("Invalid file name.\r\n")
			return
		# Specify data connection
		self.dataConnection()
		if self.clientDTP.isDataConnEstablished(): # If the data connection is open:
			# Send the FTP command for uploading
			reply = self.sendCommand("STOR " + fName + "\r\n")
			if reply == "125": # If the server reply is positive, start transfer
				self.clientDTP.toServer(fName)
			self.clientDTP.closeData() # close the data connection thereafter
			if reply != "000":
				self.receiveCommand()

# Public functions for handling the server
# ------------------------------------------------------------------------------------
	# A function to change the structure
	def changeStructure(self,struc):
		self.sendCommand("STRU " + struc + "\r\n")
	
	# A function to change the mode
	def changeMode(self,mode):
		self.sendCommand("MODE " + mode + "\r\n")

# Public functions for querying the server
# ------------------------------------------------------------------------------------
	# A function to query the server for the current directory
	def thisDirectory(self):
		self.sendCommand("PWD\r\n")

	# A function to query server OS
	def serverOS(self):
		self.sendCommand("SYST\r\n")

# Public functions to handle the directory
# -------------------------------------------------------------------------------------
 	# A function to change current working directory
	def changeDirectory(self,directory):
		self.sendCommand("CWD " + directory + "\r\n")

	# A function to change to parent directory
	def parentDirectory(self):
		self.sendCommand("CDUP\r\n")

	# A function to make a directory
	def makeDirectory(self, directory):
		self.sendCommand("MKD " + directory + "\r\n")

	# A function to remove a directory
	def removeDirectory(self, directory):
		self.sendCommand("RMD " + directory + "\r\n")

