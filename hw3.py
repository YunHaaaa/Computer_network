# Student ID : 20203110
# Name : 윤하은

from socket import *
import sys
import select
import queue

#################################################################

tcpport = sys.argv[1]

if len(sys.argv) != 2:
    print("bad input")
    exit(1)

host_name  = gethostname()
host_ip = gethostbyname(host_name)

##################################################################

def display():
    print("Student ID : 20203110")
    print("Name : HaEun Yun")

##########################################################################

display()
sys.stdout.flush()

try:
    tcpServ_sock = socket(AF_INET, SOCK_STREAM, 0)
except: # if (request_sock <0):
    print("socket() error")
    exit(1)

tcpServ_sock.setsockopt(SOL_SOCKET, SO_REUSEADDR,4)

try:
    tcpServ_sock.bind(('localhost', int(tcpport)))
except:
    print("bind() error")

try:
    tcpServ_sock.listen(5)
except:
    print("listen() error")

###################################################################

inputs = [tcpServ_sock]
outputs = []
message_queues = {}
tcpServ_sock.setblocking(0)

try:
    while inputs:
        readable, writable, exceptional = select.select(inputs, outputs, inputs)
        for s in readable:
            if s == tcpServ_sock:
                connection, client_address = s.accept()
                print("connection from host", str(client_address[0]) + ", port", str(client_address[1])+
                      ", socket", connection.fileno())
                connection.setblocking(0)
                inputs.append(connection)
                message_queues[connection] = queue.Queue()
            else:
                data = s.recv(1024)
                if data:
                    message_queues[s].put(data)
                    if s not in outputs:
                        outputs.append(s)
                    else:
                        if s in outputs:
                            outputs.remove(s)
                        inputs.remove(s)
                        s.close()
                        del message_queues[s]
                else:
                    print("Connection Closed", s.fileno())
                    inputs.remove(s)
                    exceptional.append(s)
        for s in writable:
            try:
                next_msg = message_queues[s].get_nowait()
            except queue.Empty:
                outputs.remove(s)
            else:
                for i in message_queues:
                    if i not in writable:
                        i.send(next_msg)
        for s in exceptional:
            for i in message_queues:
                i.send("good bye\r\n".encode())
            if s in outputs:
                outputs.remove(s)
            s.close()
            del message_queues[s]
except KeyboardInterrupt:
    print("Keyboard Interrupt")
    tcpServ_sock.close()
    exit(1)
except:
    print("error")
    tcpServ_sock.close()
    exit(1)