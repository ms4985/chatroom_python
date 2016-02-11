Megan Skrypek
ms4985
Programming 1

files included:

	server.py

	client.py

	user_pass.txt

to run my code:

server program is run:
--include user_pass.txt in same directory as *.py files

$ python server.py <server_port>

next, client program is run (one or many times):

$ python client.py <server_ip> <server_port>


--client will be prompted to log in
	-logging in works as specified:
		user gets 3 attempts, duplicates are rejected but dont count as attempt, user is blocked for 60 seconds when 3 attempts have beeen used, user can login again after timeout with another 3 attempts
	-once logged in user can implement any of these commands:
		$ whoelse
		$ wholast <time>
		$ broadcast message <message>
		$ broadcast user <user>...<user> message <message>
		$ message <user> <message>
		$ logout

		-time is checked to be from 0 to 60 minutes or error occurs
		-users are checked if they are currently online and valid users
	-client will be disconnected from sever if timeout occurs
	-server ctrl-c graceful exit works fine, client graceful exit sends server into infinite loop


developed from terminal using python 2.7.10
