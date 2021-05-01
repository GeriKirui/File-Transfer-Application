import socket
import threading
from ServerDTP import ServerDTP

# This file contains the implementation of the server protocol interpreter (server PI)

# A class to implement the server PI
class ServerPI(threading.Thread):
	def __init__(self, name, serverIP, serverPort, commandConnection, addr):
		# Member variables
		threading.Thread.__init__(self)
		self.name = name
		self.serverIP = serverIP
		self.cmdPort = serverPort
		self.commandConnection = commandConnection
		self.addr = addr
		self.serverDTP = ServerDTP()
		self.user = ""
		self.isUserRecognised = False
		self.isCommandActive = True
		self.possibleCommands = ["USER","PASS","PASV","PORT","SYST","RETR","STOR","QUIT",
		"NOOP","TYPE","STRU","MODE","PWD","CWD","CDUP","MKD","RMD","DELE","LIST"]
		self.noUserCommands = ["USER","NOOP","QUIT","PASS"]
		self.availableUsers = ["Ntladi","Gerald","Tshepo"]
		self.currentMode = "S"
		self.currentType = "I"

# Functions to send and receive commands
#--------------------------------------------------------------------------------	
	# A function that sends data from the server to the user
	def sendData(self, msg):
		print(msg) # print the message on terminal
		self.commandConnection.send(msg.encode()) # encode and send message

	# A function that handles the command received
	def executeCommand(self, cmd, arg):
		ftpFunction = getattr(self, cmd)
		if arg == "":
			ftpFunction()
		else:
			ftpFunction(arg)

	# A function that extracts the command from the message from the client
	def commandLength(self,cmd):
		posOfSpace = cmd.find(" ")
		size = 0
		if posOfSpace == -1:
			size = len(cmd) - 2
		else:
			size = posOfSpace

		return size

# Functions for the main server loop
# ----------------------------------------------------------------------------------
	def run(self):
		print(self.name + " connected to " + str(self.addr) + "\r\n")
		self.sendData("220 Successful control connection\r\n")
		try:
			while self.isCommandActive:
				clientMessage = self.commandConnection.recv(1024).decode()
				print(clientMessage)
				cmdLen = self.commandLength(clientMessage)
				command = clientMessage[:cmdLen].strip().upper()
				argument = clientMessage[cmdLen:].strip()
				if not self.isUserRecognised and command not in self.noUserCommands:
					self.sendData("530 Please log in\r\n")
					continue
				if command in self.possibleCommands:
					self.executeCommand(command, argument)
				else:
					self.sendData("502 Command not implemented\r\n")
		except socket.error:
			print("Terminating control connection\r\n")
			self.isCommandActive = False
			self.commandConnection.close()
			self.serverDTP.closeDataConnection()
			

# Functions for handling FTP commands
#-------------------------------------------------------------------------------------------------------------------------------------------------
	# A function that specifies the port number to be used
	def PORT(self,dataAddress):
		try:
			self.serverDTP.activateConnection(dataAddress) # activate the data connection using the specified address
			self.sendData("225 Active data connection established. \r\n") # inform the user that a connection has been established
		except:
			self.sendData("425 Can't open data connection. \r\n") # otherwise, inform the user that the connection cannot be established
			self.serverDTP.closeDataConnection()

	# A function that implements FTP USER functionality on the Server
	def USER(self,name):
		if name in self.availableUsers: # if the name is in the list of available users:
			self.user = name # the current user's name is specified by "name"
			self.serverDTP.setUser(self.user) # assign the active connection to the user who logged in
			self.sendData("331 User name okay, need password. \r\n")  # send message confirming connection to the user
		else:
			self.isUserRecognised = False # the user is not recognised by the server
			self.sendData("332 Need account for login.\r\n") # send error message to user

	# A function to verify that the data connection is active
	def NOOP(self):
		if self.isCommandActive: # If the data connection is active:
			self.sendData("200 Control connection OK. \r\n") # Inform the user that the data connection is active

	# A function which sets the representation type 
	def TYPE(self,arg):
		arg = arg.upper() # set the argument to uppercase letters
		FTPArguments = ["A","I"] # Only ASCII and Images are supported
		if arg in FTPArguments:
			if arg == "I":
				self.currentType = "I" 
				self.sendData("200 Binary (I) Type selected\r\n")
			else:
				self.currentType = "A"
				self.sendData("200 ASCII (A) Type selected\r\n")
		else:
			self.sendData("501 Invalid Type selected\r\n")

	# A function that terminates the current user
	def QUIT(self):
		self.sendData("221 Service closing control connection.\r\n") # inform the user that the data connection is being closed
		self.isCommandActive = False # do not accept further commands 
		self.commandConnection.close() # close the command connection
		self.serverDTP.closeDataConnection() # close the data connection

	# A function that specifies that file structure
	def STRU(self,arg):
		arg = arg.upper() # Set all characters to uppercase
		FTPArguments = ["F","R","P"] # Arguments allowed by FTP
		if arg in FTPArguments:
			if arg == "F": 
				self.sendData("200 File structure selected\r\n") # Inform the user that he has selected the file structure
			else:
				self.sendData("504 Command not implemented for that parameter.\r\n") # Inform the user that only File structure is implemented
		else:
			self.sendData("501 Syntax error in parameters or arguments.\r\n") # Inform the user that the parameter is not supported by FTP

	# A function that stores the specified file at the server site
	def STOR(self,file):
		try:
			self.sendData("125 Receiving " + file + " from client\r\n") # Inform the user that data is being received
			self.serverDTP.startUpload(file) # Receive the data
			self.serverDTP.closeDataConnection() # When the data transfer is over, close the data connection
			self.sendData("226 Data transfer complete " + file + " sent to server\r\n") # Inform the user that the transfer of data is complete
		except: # In case of any anomalies:
			self.serverDTP.closeDataConnection() # Close the data connection
			self.sendData("426 Unable to send file to server\r\n") # Inform the user of the failure to transfer data

	# A function that allows the user to login by using a pass-key
	def PASS(self,key = "phrase"):
		if self.user == "": # If the user has not specified his user name:
			self.sendData("530 Please log in.\r\n") # Ask the user to login
			return
		if self.serverDTP.isKeyValid(key): # If the user enters the correct key:
			# Grant access to the user 
			self.isUserRecognised = True 
			self.sendData("230 Welcome " + self.user + "\r\n") # Inform user of successful login
		else: # Otherwise, deny access
			self.isUserRecognised = False
			self.sendData("501 Invalid password\r\n") # Inform user of denied access

	# A function that makes the server listen on a data port which is not its default port and to accept the connection
	def PASV(self):
		try:
			self.serverDTP.listenPassively(self.serverIP) # Listen on the data port passively
			self.sendData("227 Entering Passive connection mode " + self.serverDTP.getPassiveServerAddr(self.serverIP) + "\r\n") # Inform the user
			self.serverDTP.acceptPassiveConnection() # Establish the connection
		except: # In case of any anomalies:
			self.sendData("425 Cannot open PASV data connection.\r\n") # Inform the user that the passive connection cannot be established
			self.serverDTP.closeDataConnection() # Close the data connection

	# A function that sets the transfer mode of data
	def MODE(self,arg):
		arg = arg.upper()
		FTPArguments = ["S","B","C"] # FTP transfer mode arguments are stream, block and compressed mode
		if arg in FTPArguments: 
			self.currentMode = "S"
			if arg == "S":
				self.sendData("200 Stream mode selected.\r\n") # Inform the user that Stream mode has been selected
			else:
				self.sendData("504 Command not implemented for that parameter.\r\n") # Inform the user that Block mode and Compressed mode are not implemented
		else:
			self.sendData("501 Syntax error in parameters or arguments.\r\n") # Inform the user that he has passed an invalid parameter

	#  A function that allows a user to change the working directory without altering login information
	def CWD(self,directoryPath):
		if directoryPath == "..":
			self.CDUP() # Change to parent directory
			return # End function
		if self.serverDTP.doesDirectoryExist(directoryPath): # If the directory exists:
			# change the current working directory to the provided directory
			self.serverDTP.changeDirectory(directoryPath)
			dir = "\"" + self.serverDTP.getCurrentDirectory() + "\""
			self.sendData("250 Working directory changed to: " + dir + "\r\n") # Inform the user of the change
		else: # If the directory does not exist:
			self.sendData("501 Provided directory does not exist. \r\n") # Inform the user that it does not exist

	# A function that changes the current working directory to the parent directory
	def CDUP(self):
		# Call the relevant function
		self.serverDTP.changeToParentDirectory()
		# Inform the user of the change of directory
		self.sendData("200 " + "Working directory changed to: " + "\"" + self.serverDTP.getCurrentDirectory() + "\"\r\n")

	# A function that informs the user of the operating system for which the server is designed. 
	def SYST(self):
		# Inform the user that server supports Linus OS
		self.sendData("215 UNIX system type. \r\n")

	# A function that makes the directory specified by the path
	def MKD(self,directoryPath):
		# if the specified directory does not exist:
		if not self.serverDTP.doesDirectoryExist(directoryPath):
			self.serverDTP.makeDirectory(directoryPath) # make the directory
			self.sendData("257 Directory created. " + "\r\n") # Inform the user that the directory has been created
		else: # Otherwise
			self.sendData("501 Directory already exists. \r\n") # Inform the user that the directory already exists

	# A function that deletes the file present at the file path
	def DELE(self,path):
		# First check if the file exists at the specified path
		if self.serverDTP.doesFileExist(path):
			self.serverDTP.deleteFile(path) # delete the file at the path
			self.sendData("250 File successfully deleted.\r\n")
		else:
			self.sendData("501 File does not exist.\r\n")

	# A function that retrieves a copy of a specified file if it exists on the server
	def RETR(self,file):
		if self.serverDTP.doesFileExist(file): # If the file exists on the Server:
			try:
				self.sendData("125 Sending " + file + " to client\r\n") # Inform the user that the file is being transferred
				self.serverDTP.startDownload(file) # Start the download from the server to the user
				self.serverDTP.closeDataConnection() # When the data has been sent, close the connection
				self.sendData("226 Data transfer complete: " + file + " sent to client\r\n") # Inform the user that the data transfer has been completed
			except: # If anomalies occur during the transfer of data
				self.serverDTP.closeDataConnection() # Close the data connection
				self.sendData("426 Unable to send file to client\r\n") # Inform the user that the data could not be transferred successfully
		else:
			self.sendData("450 Invalid file\r\n") # If the file does not exist on the folder, inform the user
			self.serverDTP.closeDataConnection() # close the data connection

	# A function that causes a list to be sent from the server to the client
	def LIST(self,dirPath = ""):
		if dirPath == "":
			dirPath = self.serverDTP.getCurrentDirectory()
		print(dirPath + "\r\n")
		if self.serverDTP.doesDirectoryExist(dirPath):
			try:
				self.sendData("125 Sending file list\r\n")
				self.serverDTP.sendList(dirPath)
				self.serverDTP.closeDataConnection()
				self.sendData("226 List successfully sent\r\n")
			except:
				self.serverDTP.closeDataConnection()
				self.sendData("426 Unable to send list to client\r\n")
		else:
			self.sendData("450 Invalid file path\r\n")
			self.serverDTP.closeDataConnection()

	# A function that removes the specified directory 
	def RMD(self,directoryPath):
		# First check that the directory exists in the first place
		if self.serverDTP.doesDirectoryExist(directoryPath):
			# If it exists, delete it
			self.serverDTP.deleteDirectory(directoryPath)
			self.sendData("250 Directory successfully deleted.\r\n") # Inform the user of the deletion
		else: # If the directory does not exist on the system
			self.sendData("501 No such directory on system.\r\n") # Inform the user that it does not exist

	# A function that prints the current working directory for the user
	def PWD(self):
		dir = "\"" + self.serverDTP.getCurrentDirectory() + "\""
		self.sendData("200 " + "Current working directory: " + dir + "\r\n")

