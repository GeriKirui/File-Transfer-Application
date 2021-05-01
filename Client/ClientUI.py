from cmd import Cmd
import mainClient

# The User-Interface (UI) of the FTP Application

class MyPrompt(Cmd):
	prompt = 'user_input> ' # A prompt for user input 
	intro = "Welcome to the FTP Application! Type ? to list all possible commands." # The welcome-line of the app

	# A UI function to return a list of the files in the working directory
	def do_list(self,dir):
		'''Get a list of all files at the specified path.'''
		# Update the list in the server
		mainClient.client.updateRemoteDirectoryList()
		# Get the updated list from the server
		data = mainClient.client.getRemoteDirectoryList()
		line = "-" * 90
		print(line)
		print("{:<20s}{:<20s}{:<20s}{:<20s}".format("Name", "Size", "Date Modified", "Type"))
		print(line)
		for item in range(len(data)):
			if data[item][3][0] == "d":
				data[item][3] = "directory"
			else:
				data[item][3] = "file"
			print("{:<20s}{:<20s}{:<20s}{:<20s}".format(data[item][0],data[item][1], data[item][2],data[item][3]))
		print("\r\n")

	# A UI function to delete a file.
	def do_delete(self,filename):
		'''Delete an existing file. You should enter the name of the file and the extension after this command, separated by a space.'''
		mainClient.client.delete(filename)

	# A UI function to remove the specified directory
	def do_remove_dir(self,pathname):
		'''Remove an existing directory. You should enter the pathname after this command, separated by a space.'''
		mainClient.client.removeDirectory(pathname)

	# A UI function to create a directory
	def do_make_dir(self,pathname):
		'''Make a directory. You should enter the pathname after this command, separated by a space.'''
		mainClient.client.makeDirectory(pathname)

	# A UI function to return to the parent directory
	def do_parent_dir(self,inp):
		'''Return to the parent directory.'''
		mainClient.client.parentDirectory()

	# A UI function to change the working directory
	def do_change_dir(self,dir):
		'''Change the current working directory. You should enter the pathname after this command, separated by a space.'''
		mainClient.client.changeDirectory(dir)

	# A UI function to print the current working directory
	def do_this_dir(self, inp):
		'''Find out the current working directory'''
		mainClient.client.thisDirectory()

	# A UI function to return the system type
	def do_os(self,inp):
		'''Find out the OS of the Server. You need to login first.'''
		mainClient.client.serverOS()

	# A UI function to verify that the connection is open
	def do_ping(self, inp):
		'''Check whether the connection to the server is OK.'''
		mainClient.client.ping()

	# A UI function to upload a file from the local host to the server
	def do_upload(self,file):
		'''Upload a file to the server to local host. You should enter the filename and the extension after this command, separated by a space.'''
		mainClient.client.upload(file)

	# A UI function to download a file from the server to the local host
	def do_download(self,file):
		'''Download a file from the server to local host. You should enter the filename and the extension after this command, separated by a space.'''
		mainClient.client.download(file)

	# A UI function to logout of the application
	def do_quit(self, inp):
		'''Logout of the application.'''
		mainClient.client.exit()

	# A UI function to login to the application
	def do_login(self, arg):
		'''Log into the application. You should provide your username after this command, separated by a space.'''
		mainClient.client.login(arg)


MyPrompt().cmdloop()