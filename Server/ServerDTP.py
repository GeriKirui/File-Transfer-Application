import socket
import random
import os
import datetime
import stat

# This file contains the implementation of the server data transfer protocol (server DTP)

# A class to implement the server DTP
class ServerDTP():
	def __init__(self):
		# Member variables
		self.dataConnection = None
		self.dataSocket = None
		self.files = None
		self.user = None
		self.currentDirectory = None
		self.rootDirectory = None
		self.dataPort = None
		self.dataPortUpper = None
		self.dataportLower = None
		self.isConnectionOpen = False
		self.isConnectionPassive = False
		self.bufferSize = 1024

# Functions for the establishement of a passive data connection
#-------------------------------------------------------------------------------------------------------
	# A function that obtains the server's address from the specified host
	def getPassiveServerAddr(self,host):
		serverAddress = host.split(".")
		serverAddress = ",".join(serverAddress)
		serverAddress = "(" + serverAddress + "," + self.dataPortUpper + "," + self.dataportLower + ")"
		return serverAddress

	# A function that accepts a passive connection from the user
	def acceptPassiveConnection(self):
		self.dataConnection,dataAddr = self.dataSocket.accept() # accept the connection
		# Set associated boolean variables to True
		self.isConnectionOpen = True
		self.isConnectionPassive = True

	# A function that makes the server listen on the port passively
	def listenPassively(self,host):
		self.generatePassiveDataPort() # generate a random port number
		self.dataSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # Establish a TCP connection
		self.dataSocket.bind((host,self.dataPort)) # Bind the host name and the port number
		self.dataSocket.listen(1) # Listen on the port

	# A function that generates a random port number for the connection
	def generatePassiveDataPort(self):
		self.dataPortUpper = str(random.randint(20,30))
		self.dataportLower = str(random.randint(0,255))
		self.dataPort = (int(self.dataPortUpper) * 256) + int(self.dataportLower)

# Functions for the establishment of an active data connection
#-------------------------------------------------------------------------------------
	# A function that extracts the ip address of the user
	def extractActiveUserIPAddress(self,dataAddress):
		splitAddress = dataAddress.split(',')
		userIP = '.'.join(splitAddress[:4])
		return userIP

	# A function that extracts the port number of the user
	def extractActiveUserPort(self,dataAddress):
		splitAddress = dataAddress.split(',')
		port = splitAddress[-2:]
		self.dataPort = (int(port[0]) * 256) + int(port[1])
		return self.dataPort

    # A function that establishes a connection		
	def activateConnection(self,dataAddress):
		ipAddress = self.extractActiveUserIPAddress(dataAddress) # extract the user's ip address
		port = self.extractActiveUserPort(dataAddress) # extract the user's port number
		self.dataConnection = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # setup a connection
		self.dataConnection.connect((ipAddress,port)) # establish the connection
		self.isConnectionOpen = True
		self.isConnectionPassive = False

# Functions for handling the data connection
# ------------------------------------------------------------------------------------
	# A function that opens the data connection
	def data_connection(self,dataConnection):
		self.isConnectionOpen = True
		self.dataConnection = dataConnection

	# A function that closes the data connection
	def closeDataConnection(self):
		if self.isConnectionOpen and self.dataConnection != None:
			self.dataConnection.close()
			print("Terminating data connection\r\n")

# Getter functions for the system server (querying functions)
#------------------------------------------------------------------------------------------------------------------------------------------------
	# A function to determine the path from the root directory
	def pathFromRoot(self,path):
		if path[0] != "/": # If '/' is not present in the beginning of the directory:
			path = self.rootDirectory + self.currentDirectory + path # the path is concatenated with the root directory plus the current directory 
		else:
			path = self.rootDirectory + path # the path is concatenated with the root directory only
		return path

	# A function to check whether the file exists in the Server
	def doesFileExist(self,fPath):
		fPath = self.pathFromRoot(fPath) # find the path of the file
		if os.path.isfile(fPath): # check if the file exists
			return True
		return False

	# A function that gets the current working directory
	def getCurrentDirectory(self):
		return self.currentDirectory

	# A function that checks whether the directory exists on the system
	def doesDirectoryExist(self,directoryPath):
		directoryPath = self.pathFromRoot(directoryPath) # Find the directory relative to the root directory
		print("DTP Path = " + directoryPath + "\r\n")
		if os.path.isdir(directoryPath): # If the directory is found:
			return True # Return true
		return False # Otherwise, return false

	# A function that checks whether the pass-key entered is valid
	def isKeyValid(self,key):
		keyPath = "UserFiles/" + self.user + "/Phrase.txt" # locate the correct password in the server
		file = open(keyPath,"r") # open the file containing the correct password
		text = file.readlines() # Read the text in the file
		file.close() # Close the file
		if key in text: # If the key is in the text:
			return True # The key is valid
		else:
			return False # otherwise, it is invalid

# Setter functions for the file system
#---------------------------------------------------------------------------------------------------------------
	# A function to assign the active connection to the current user
	def setUser(self,name):
		self.user = name # set the current user's name
		self.rootDirectory = "UserFiles/" + self.user + "/Files" # change the directory to the user's directory
		self.currentDirectory = "/"

	# A function that changes the current working directory to the parent directory
	def changeToParentDirectory(self):
		# Split the current working directory by the appearance of '/'
		parentDirectory = self.currentDirectory.split("/")
		parentDirectory = "/".join(parentDirectory[0:-2]) + "/"
		if parentDirectory[0] != "/": # If the first element of the parent directory is not '/':
			# Append it to the parent directory
			parentDirectory = "/" + parentDirectory
		self.currentDirectory = parentDirectory # Otherwise, it is simply the current working directory

	# A function that deletes the file at the path
	def deleteFile(self,path):
		# Find the path relative to the root directory
		path = self.pathFromRoot(path)
		os.remove(path) # Remove the file at the path

	# A function that removes the specified directory
	def deleteDirectory(self,directoryPath):
		# Find the path of the directory relative to the root directory
		directoryPath = self.pathFromRoot(directoryPath) 
		# Remove the directory
		os.rmdir(directoryPath)

	# A function for making a directory specified by directoryPath
	def makeDirectory(self,directoryPath):
		# Find the desired path relative to the root
		directoryPath = self.pathFromRoot(directoryPath)
		os.mkdir(directoryPath) # make the directory

	# A function that changes the working directory of the system
	def changeDirectory(self,directoryPath):
		# Append '/' to the end initial directory
		directoryPath = directoryPath + "/"
		if directoryPath[0] != "/": # If the first element of the directory path is not '/':
			self.currentDirectory = self.currentDirectory + directoryPath # the directory path is appended to the current directory
		else: # Otherwise
			self.currentDirectory = directoryPath # The current working directory is changed to the provided directory

# Functions that facilitate the transfer of data
#----------------------------------------------------------------------------------------------------------------
	# A function that facilitates the receipt of the file throught the data connection
	def startUpload(self,fName):
		fName = self.rootDirectory + self.currentDirectory + fName # Append the name of the file to the directory
		file = open(fName,"wb") # Opening a file to write in binary mode
		writeFile = self.dataConnection.recv(self.bufferSize) # Start receiving binary from the user
		while writeFile: # while the data is being transferred:
			file.write(writeFile)  # Write the data to the file
			writeFile = self.dataConnection.recv(self.bufferSize) # Receive next data
		file.close() # close the file. The transfer is complete

	# A function that initiates the download of files
	def startDownload(self,fileName):
		fileName = self.rootDirectory + self.currentDirectory + fileName
		file = open(fileName,"rb")
		readingFile = file.read(self.bufferSize)
		while readingFile:
			self.dataConnection.send(readingFile)
			readingFile = file.read(self.bufferSize)
		file.close()

	# A function that sends the directory list to the client
	def sendList(self,dirPath):
		dirList = []
		currentDirectory = self.rootDirectory + self.currentDirectory
		items = os.listdir(currentDirectory)
		for file in items:
			newPath = os.path.join(currentDirectory,file)
			dateModified = datetime.datetime.fromtimestamp(os.path.getmtime(newPath)).strftime("%b %d %H:%M")
			fileStats = os.stat(newPath)
			linkNum = fileStats.st_nlink
			userID = fileStats.st_uid
			groupID = fileStats.st_gid
			fileSize = os.path.getsize(newPath)
			fileData = str(stat.filemode(os.stat(newPath).st_mode)) + "\t" + str(linkNum) + "\t" + str(userID) + "\t" + str(groupID) + "\t\t" + str(fileSize) + "\t" + str(dateModified) + "\t" + file 
			dirList.append(fileData)
		for item in dirList:
			self.dataConnection.send((item + "\r\n").encode())
