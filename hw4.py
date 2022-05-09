# Student ID : 20203110
# Name : 윤하은

from socket import *
import sys
import select
import queue

#################################################################

if len(sys.argv) != 3:
    print("Usage : %s <tcpport> <userid>\n"%sys.argv[1])
    exit(1)

tcpport = sys.argv[1]
userid = sys.argv[2]

##################################################################

def display():
    print("Student ID : 20203110")
    print("Name : HaEun Yun")

peertcpSocket = -1 # peer socket
command = {}

display()
sys.stdout.flush()

##########################################################################

#  NEED TO CREATE A SOCKET FOR TCP SERVER
try:
    tcpServ_sock = socket(AF_INET, SOCK_STREAM, 0)
except:
    print("socket() error")
    exit(1)

tcpServ_sock.setsockopt(SOL_SOCKET, SO_REUSEADDR,4)


#  NEED TO bind
try:
    tcpServ_sock.bind(('localhost', int(tcpport)))
except:
    print("bind() error")


#  NEED TO listen
try:
    tcpServ_sock.listen(5)
except:
    print("listen() error")

###################################################################

# initialize the select mask variables and set the
# mask with stdin and the tcp server socket

fd_max = [sys.stdin.fileno(), tcpServ_sock.fileno()]
socketno = {tcpServ_sock.fileno():tcpServ_sock, sys.stdin.fileno():sys.stdin}
temps = []
message_queues = {}
tcpServ_sock.setblocking(0)

host_name = ''
connect = 0
try:
    i = 0
    while fd_max:
        readable, writable, exceptional = select.select(fd_max, temps, fd_max, None)
        for x in readable:

            if x == tcpServ_sock.fileno():
                # Input from the keyboard
                print("%s>" % userid)
                # NEED TO IMPLEMENT for input from keybord
                connection, client_address = tcpServ_sock.accept()
                print("connection from host", str(client_address[0]) + ", port", str(client_address[1]) +
                      ", socket", connection.fileno())
                connection.setblocking(0)

                connection.send(userid.encode())
                host_name = connection.recv(1024).decode()

                fd_max.append(connection.fileno())
                socketno[connection.fileno()] = connection
                message_queues[connection.fileno()] = queue.Queue()
                connect = 1

            elif x == sys.stdin.fileno(): # connection.fileno():
                print("%s>"%userid)
                # connect request from a peer
                read = sys.stdin.readline()
                read_s = read.strip().split()

                if read_s[0] == "@talk":
                    host_port = int(read_s[2])
                    client_socket = socket(AF_INET, SOCK_STREAM, 0)
                    client_socket.connect(('localhost', host_port))

                    client_socket.send(userid.encode())
                    host_name = client_socket.recv(1024).decode()

                    socketno[client_socket.fileno()] = client_socket
                    fd_max.append(client_socket.fileno())
                    message_queues[client_socket.fileno()] = queue.Queue()
                    connect = 1
                elif not connect:
                    print("no connection")
                elif read:
                    try:
                        socketno[fd_max[-1]].send(read.encode())
                    except:
                        print("broken pipe")
                    if read.strip() == "@quit":
                        exit(1)
                        socketno[fd_max[-1]].close()

            else: # if x == peertcpSocket:
                # message from a peer
                data = socketno[x].recv(1024).decode()
                if data.strip() == "@quit":
                    socketno[x].close()
                    fd_max.remove(x)
                    print("Connection Closed", x)
                    connect = 0
                elif data:
                    print("%s : " % host_name, data)
                    message_queues[x].put(data)
                    if x not in temps:
                        temps.append(x)
                    else:
                        if x in temps:
                            temps.remove(x)
                        fd_max.remove(x)
                        socketno[x].close()
                        connect = 0
                        del message_queues[x]
                        tcpServ_sock.setblocking(0)

                else:
                    socketno[x].close()
                    fd_max.remove(x)
                    tcpServ_sock.setblocking(0)

        for x in writable:
            try:
                next_msg = message_queues[x].get_nowait()
            except queue.Empty:
                temps.remove(x)
            else:
                for i in message_queues:
                    if i not in writable:
                        socketno[i].send(next_msg)
        for x in exceptional:
            for i in message_queues:
                socketno[i].send(("Connection Closed" + str(x) + "\r\n").encode())
            if x in temps:
                temps.remove(x)
            socketno[x].close()
            tcpServ_sock.setblocking(0)
            del message_queues[x]

except KeyboardInterrupt:
    print("Keyboard Interrupt")
    tcpServ_sock.close()
    exit(1)
except:
    tcpServ_sock.close()
    exit(1)
