import socket
import sys
import select
import threading
import time

SIZE = 4096
TIME_OUT = 1800

#tells server to logout and exits
def logout(socket):
	print "\n client logging out. . ."
	socket.send("logout")
	sys.exit()

#called by thread when timeout occurs, function calls regular logout fn
def inactive_logout(socket):
	print "\n automatically logged out due to inactivity"
	logout(socket)

#setup client socket
Host, Port = sys.argv[1], int(sys.argv[2])
csock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

try:
	print "connecting. . ."
	csock.connect((Host, Port))
except:
	print "no server on Host/Port"
	sys.exit()

connected = False
while 1:
	sockets = [sys.stdin, csock]
	read, write, error = select.select(sockets, [], [])
	try:
		#if server sent data
		for socket in read:
			if socket == csock:
				received = socket.recv(SIZE)
				if not received:
					print "\n Server disconnected"
					sys.exit()
				elif "WELCOME" in received:
					print ">> {}".format(received)
					connected = True

					#used to check time in order to implement autologout
					cur_t = threading.Timer(TIME_OUT, inactive_logout, [socket])
					cur_t.start()

					sys.stdout.write("~*~ ")
					sys.stdout.flush()
				else:
					print ">> {}".format(received)
					sys.stdout.write("~*~ ")
					sys.stdout.flush()
					if connected == True:

						#since client is connected, check if inactive for TIME_OUT
						cur_t.cancel()
						cur_t = threading.Timer(TIME_OUT, inactive_logout, [socket])
			
			#prompt user for data and send any that exists
			else:
				message = sys.stdin.readline()
				if message:
					csock.send(message)
				sys.stdout.write("~*~ ")
				sys.stdout.flush()
		
	#catch ctrl-c exits			
	except (KeyboardInterrupt, SystemExit):
		logout(csock)
sys.exit()


