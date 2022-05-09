# Student ID : 20203110
# Name : 윤하은
# Python TCP Server
from socket import *
import sys

if len(sys.argv) != 2:
    print(len(sys.argv))
    print("usage : %s portnum"%(sys.argv[1]), file=sys.stderr)# sys.stderr.write())
    exit(1)

portnum = int(sys.argv[1])

print("Student ID : 20203110")
print("Name : HaEun Yun")

# Create a Server Socket
try:
    serverSocket = socket(AF_INET, SOCK_STREAM, IPPROTO_TCP)
except:
    serverSocket = socket(AF_INET, SOCK_STREAM, IPPROTO_TCP)
    print("socket error")
    exit(1)

try:
    serverPort = int(sys.argv[1])
    serverSocket.bind(('', serverPort))
except:
    print("bind error")
    serverSocket.close()
    exit(1)

try:
    serverSocket.listen(1)
except:
    print("listen error")
    serverSocket.close()
    exit(1)


while(True):
    # a new connection is available on the connection socket
    connectionSocket, addr = serverSocket.accept()
    if connectionSocket:
        pass
    else:
        print("accept error")
        serverSocket.close()
        break

    conn = str(connectionSocket).split(', ')
    socketnum = conn[0][len(conn[0])-1]
    portnum = conn[len(conn)-1].split(')>')[0]
    hostp = conn[len(conn)-2].split('\'')[1]
    print("Connection : Host IP " + hostp + " Port " + portnum + ", socket " + socketnum)

    # recv request, send responce msg and file
    while(True):
        data = connectionSocket.recv(1024)
        dataLen = len(data)
        if dataLen <= 0:
            try:
                connectionSocket.close()
                break
            except:
                print("close error")
                break

        DATA = data.split(b'\r\n')
        header = len(DATA)
        for d in DATA:
            print(d.decode())

        print(header-3, "headers")
        file = DATA[0].split(b' ')[1].split(b'/')[1].decode()
        responce = []
        try:
            f = open(file, "r")
        except:
            print("Server Error : No such file "+ file + "!")
            responce.append("HTTP/1.0 404 NOT FOUND\r\n")
            responce.append(" Connection: close\r\n")
            responce.append("Content-Length: 0\r\n")
            responce.append("Content-Type: text/html\r\n\r\n")
            for i in responce:
                connectionSocket.send(i.encode())
            connectionSocket.close()
            break

        fileLen = 0
        line = f.readline()
        while line:
            fileLen += len(line)
            line = f.readline()
        responce = []
        responce.append("HTTP/1.0 200 OK\r\n")
        responce.append("Connection: close\r\n")
        responce.append("Content-Length: " + str(
            fileLen) + "\r\n")
        responce.append("Content-Type: text/html\r\n\r\n")
        for i in responce:
            connectionSocket.send(i.encode())

        f = open(file, "r")
        sendLen = 0
        line = f.readline()
        while line:
            connectionSocket.send(line.encode())
            sendLen += len(line)
            line = f.readline()

        print("finish", fileLen, sendLen)
        f.close()
    connectionSocket.close()





