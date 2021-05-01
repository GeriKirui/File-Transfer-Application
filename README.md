# ELEN4017-Network Fundamentals
## File Transfer Application

1. Login credentials (Username, Password)
  * Gerald, 1615002
  * Ntladi, 1599953
  * Tshepo, 1705890

2. To run the server, run the following in command line: 
``` cmd
py mainServer.py
```
  * _You must run the server before the client_

3. To run the client, run the following in command line:
``` cmd
py ClientUI.py
```
    #---------------------------- User Interface -----------------------------------------------

  * For a list of all commands, use `help`

  * To login, use `login *name* *password*`. Note the spaces.

  * To logout, press `quit`.

  * To download a file, use `download *filename.extension*.` Note the space between the command and the filename. 

  * To upload a file, use `upload *filename.extension*.` Note the space between the command and the filename.

  * To delete an existing file, use `delete *filename.extension*.` Note the space between the command and the filename.

  * To check whether connection is OK, use `ping`.

  * To find out the OS of the Server, use `os`.

  * To find out about the current working directory, use `this_dir`.

  * To change the current working directory, use `change_dir *pathname*`. Note the space between the command and the pathname.

  * To return to the parent directory, use `parent_dir`.

  * To make a directory, use `make_dir *pathname*`. Note the space between the command and the pathname.

  * To remove a directory, use `remove_dir *pathname*`. Note the space between the command and the pathname.

  * To list all files in the current working directory, use `list`.

  __*Only the default states for structure (f) and mode (s) have been implemented__