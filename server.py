import socket
import sys
import select
import time

SIZE = 4096
Connections = []
valid_logins = {}
currently_online = {}
user_login_attempts = {} # dict[user_address[1]] = # of login attempts remaining (default: 3)
BLOCK_TIME = 60
blocked_users = {}
HOUR = 3600
user_login_time = {}


def check_login(socket,address):
	print "checking client authorization. . ."
	#if socket is new user give them 3 login attempts
	if check_if_new_user(socket) == True:
		user_login_attempts[socket] = 3
	#check if user is valid
	auth = search_users(socket, address)
	#decrement login attempts and try again
	while auth == False:
		if user_login_attempts[socket] > 1:
			user_login_attempts[socket] -= 1
			socket.sendto("login error! " + "attempts remaining: " + str(user_login_attempts[socket]) + "\n", address)
			auth = search_users(socket, address)
		elif user_login_attempts[socket] == 1:
			socket.sendto("login failed! you have been blocked\n please try again in 60 seconds\n", address)
			blocked_users[address] = time.time()
			user_login_attempts[socket] = -1
			auth = search_users(socket, address)
		else:
			auth = search_users(socket, address)
	#user has logged in successfully at this point
	socket.sendto("Login successful! WELCOME", address)
	del user_login_attempts[socket]
	user_login_time[socket] = time.time()
	print "new client logged in" , socket
	Connections.append(socket)
	return True

def search_users(socket, address):
	socket.sendto("enter login info in form: username password", address)
	login = socket.recv(SIZE)
	login = login.split()
	#first check if have been blocked
	if check_if_blocked(socket,address) == True:
		socket.sendto("You are still blocked!\n", address)
		return False
	#check if username and password is valid
	else:
		for x in valid_logins.keys():
			if x == login[0]:
				#make sure user isnt already logged in
				for user in currently_online.values():
						if user == login[0]:
							socket.sendto("this user is currently logged in\n", address)
							#increment login attempts here so it doesnt count against the user later
							user_login_attempts[socket] += 1 
							return False
				#login is valid
				if valid_logins[x] == login[1]:
					currently_online[socket] = login[0]
					return True
	#if reached this point the login is invalid
	return False

def check_if_blocked(socket, address):
	#check if user is blocked
	for x in blocked_users.keys():
		if x == address:
			current_time = time.time()
			# if user is blocked, check if still should be blocked
			if (current_time - blocked_users[address]) <= 60:
				return True
			# if 60 seconds has passed, unblock user and reset login attempts
			else:
				socket.sendto("congrats! you're not blocked anymore!", address)
				del blocked_users[address]
				user_login_attempts[socket] = 3
				return False
	return False

#new user helper function
def check_if_new_user(socket):
	for x in user_login_attempts.keys():
		if x == socket:
			return False
	return True

# parses the commands sent in by the client
def handle_client(socket,address):
	try:
		try:
			#if server has received a command
			received = socket.recv(SIZE)
			received = received.split()
			command = received[0]

			if command == "broadcast":

				if received[1] == "message":
					b_message = " ".join(received[2:])
					broadcast(socket, b_message)

				if received[1] == "user":
					i = 2
					user_list = []
					while received[i] != "message":
						user_list.append(received[i])
						i += 1
					bu_message = " ".join(received[i+1:])
					broadcast_user(socket, user_list, bu_message)

			elif command == "message":
					user = received[1]
					message = " ".join(received[2:])
					private_msg(socket, user, message)

			elif command == "whoelse":
				whoelse(socket)

			elif command == "wholast":
				time = received[1]
				wholast(socket, time)

			elif command == "logout":
				logout(socket)

			#send if the command is incorrect	
			else:
				socket.send("ERROR: not a valid command, try again")

		#print after helper functions have completed		
		finally:
			print "handled client", socket

	#if nothing is received handle something else
	except:
		pass

def broadcast(socket, message):
	for sock in Connections:
		if sock != server and sock !=socket:
			try:
				#try and send the broadcast to online users
				sock.send(currently_online[socket] + ": " + message)

			except:
				#user has been disconnected to close it
				sock.close()
				Connections.remove(sock)

		#broadcast message on sender's socket prints as me: message
		elif sock != server and sock ==socket:
			sock.send("me: " + message)

def broadcast_user(socket, user_list, message):
	#keeps record of users and whether they exist or not
	user_exists = {}
	for user in user_list:
		user_exists[user] = False
		for sock in currently_online.keys():
			#put user in dictionary with value True and send message
			if currently_online[sock] == user:
				user_exists[user] = True
				sock.send(currently_online[socket] + ": " + message)
	#tell sender which users dont exist/arent online
	for user in user_exists.keys():
		if user_exists[user] == False:
			socket.send("ERROR: " + user + " either offline or doesnt exist")


def private_msg(socket, user, message):
	user_exists = False
	for sock in currently_online.keys():
		#check is user is valid
		if currently_online[sock] == user:
			user_exists = True
			#if so then send the message
			sock.send("PRIVATE MSG FROM " + currently_online[socket] + ": " + message)
	#the user isnt online or doesnt exist
	if user_exists == False:
		socket.send("ERROR: user either offline or doesnt exit")		

def whoelse(socket):
	socket.send("online users: ")
	#iterate through online users and send usernames
	for x in currently_online.values():
		if x != currently_online[socket]:
			socket.send("\n\t" + x)

def wholast(socket, t):
	#check if valid time
	if ((int(t) > 0) & (int(t) < 3600)):
		min = float(int(t)/60)
		socket.send("users online within " + str(min) + " minutes")
		#iterate through online user login times 
		for x in user_login_time.keys():
			ct = time.time()
			#if online within time send to socket
			if ((ct - int(t)) <= user_login_time[x]):
				user = currently_online[x]
				socket.send("\n\t" + user)
	else:
		socket.sent("ERROR: time must be from 0 to 60 minutes")


def logout(socket):
	#cleanup dictionaries and disconnect user
	del currently_online[socket]
	del user_login_time[socket]
	Connections.remove(socket)
	socket.close()

					
def shutdown():
	print "\n server shutting down. . ."
	server.close()
	sys.exit()


#read logins from user_pass.txt

file = "user_pass.txt"
with open(file, 'r') as f:
	for line in f.readlines():
		combos = line.split()
		for x in combos:
			valid_logins[combos[0]] = combos[1]

#create server socket 
Host, Port = '', int(sys.argv[1])
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((Host,Port))
print "server running on: ", Host
server.listen(10)
print "server listening for clients. . ."
Connections.append(server)

try:
	while 1:
		read, write, error = select.select(Connections, [], [])
		for sock in read:
			if sock == server:					
				socket, address = server.accept()
				check_login(socket,address)
			else:
				try:
					handle_client(sock,address)
				except:
					sock.close()
#try and catch ctrl-c
except (KeyboardInterrupt, SystemExit):
	shutdown()
server.close()


	

