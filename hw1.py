# Student ID : 20203110
# Name : 윤하은
# http://netapp.cs.kookmin.ac.kr/member/palladio.JPG
from socket import *


def PROMPT():
    inp = input(">")
    return inp


_GETCMD = "get"
_QUITCMD = "quit"

###########################
socketserver = -1
buf = []

fname = []

print("Student ID : 20203110")
print("Name : Haeun Yun")
print()



while (True):
    cmd = PROMPT()
    if not cmd.strip():
        print("error - cmd input")
        continue
    elif cmd == _QUITCMD:
        exit(0)

    cmdlist = []
    cmdlist = cmd.split()

    getCmd = cmdlist[0] # = get
    urlCmd = cmdlist[1] # = http://~~~

    if getCmd.strip() != _GETCMD:
        print("Wrong command %s", cmd)
        continue

    ##################################################

    hostp = gethostbyname(getfqdn())
    hostn = gethostbyaddr(hostp)
    serverPort = getservbyname(urlCmd.split(':')[0])
    serverName = getservbyport(serverPort)

    urlCmdLst = urlCmd.split("/", 3)

    if serverName != "http":
        print("Only support http, not", serverName)
        print()
        continue

    url = ""

    if len(urlCmdLst[2].split(':')) >= 2:
        serverPort = urlCmdLst[2].split(':')[1]
        urlCmdLst[2] = urlCmdLst[2].split(':')[0]
        urlCmdLst.insert(3, serverPort)
        url = urlCmd
        serverPort = int(serverPort)
    else:
        urlCmdLst.insert(3, ":"+str(serverPort))
        for i in range(len(urlCmdLst)):
            url += urlCmdLst[i]
            if i == 2 or i == len(urlCmdLst)-1:
                pass
            else:
                url += "/"


    ###########   connect to a server   ##############

    try:
        clientSocket = socket(AF_INET, SOCK_STREAM, IPPROTO_TCP)
        #sin_family = AF_INET
        #sin_port = htons(pn)
        clientSocket.bind((hostp, serverPort))
    except:
        print("socket error")
        continue


    host = urlCmdLst[2] + urlCmdLst[3] + "\r\n"
    try :
        clientSocket.connect((urlCmdLst[2], serverPort))
    except :
        print(urlCmdLst[0].split(":")[0], urlCmdLst[2], urlCmdLst[2], serverPort, urlCmdLst[4])
        print(urlCmdLst[2], ": unknown host")
        print("cannot connect to server", urlCmdLst[2], serverPort)
        print()
        clientSocket.close()
        continue


    GET = "/" + urlCmdLst[4]
    Host = urlCmdLst[2]
    UserAgent = "HW1/1.0"
    Connection = "close"

    rn = "\r\n"

    requestmsg = "GET " + GET + " HTTP/1.0" + rn + "Host:" + Host + rn + "User-Agent:" + UserAgent + rn + "Connection:" + Connection + rn + rn
    print(requestmsg)

    lastp = urlCmdLst[len(urlCmdLst)-1].split('/')
    fname = lastp[len(lastp)-1]

    try:
        f = open(fname, "wb")
    except:
        print("file open error")
        clientSocket.close()
        continue

    request = clientSocket.send(requestmsg.encode())
    data = clientSocket.recv(1024)
    i = 1

    current = 0
    count = 1

    w = data.split(b'\r\n\r\n')
    header = w[0]
    w = w[1]

    if (int(header.split()[1]) != 200):
        print(header.split(b'\r\n')[0].split(b' ', 1)[1].decode())
        clientSocket.close()
        continue

    for hline in header.split(b'\r\n'):
        lst = hline.split(b' ')
        for i in range(0, len(lst)):
            if lst[i].decode() == "Content-Length:":
                size = int(lst[i+1])

    print("Total Size", size, "bytes")

    try:
        while (data):
            f.write(w)
            current += len(w)
            if current / size * 100 >= count*10:
                print("Current Downloading %d/%d (bytes) %s%%"%(current, size, int(current / size * 100)))
                count += 1
            clientSocket.send(data)
            data = clientSocket.recv(1024)
            w = data
            i += 1
    except:
        print("file download error")
        clientSocket.close()
        f.close()
        continue

    print("Download Complete: %s, %d/%d"%(fname, size, size))

    f.close()
    clientSocket.close()