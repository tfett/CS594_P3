import socket

#from command line arguments
import sys

url = sys.argv[1]
fName = sys.argv[2]

DEBUG = False

#extract the hostname
if (url[0:11] == "http://www."):
    url = url[11:]
if (url[0:7] == "http://"):
    url = url[7:]
if (url[0:3] == "www"):
    url = url[4:]

locN = url.find("/")

if (locN == -1):
    url += "/"
    fileN = url[locN:]
    url = url[:locN]
else:
    fileN = url[locN:]
    url = url[:locN]



if (fileN[-1] == "/"):
    fileN = fileN + "index.html"


#DNS lookup to retrieve the IP address for the server using
TCP_IP = socket.gethostbyname(url)


TCP_PORT = 80 
BUFFER_SIZE = 1028


s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((TCP_IP, TCP_PORT))
#Submit a valid HTTP 1.1 request for the desired URL
MESSAGE = "GET " + fileN + " HTTP/1.1\r\n"
MESSAGE += "Host: " + url + " \r\n\r\n"

s.send(MESSAGE)




#actual stuff got saze to the file
data = s.recv(BUFFER_SIZE)

hSize = data.find("\r\n\r\n")+4
header = data[:hSize]



#check success
if DEBUG:
    print data
if (header[9:12] == "200"):
    data = data[hSize:]
    fileSize = header.find("Content-Length: ") + 16
    sizeEnd = header[fileSize:].find("\n")

    sizeOfFile = header[fileSize:fileSize+sizeEnd]
    sizeOfFile = int(sizeOfFile)

    
    recvCount = sizeOfFile/BUFFER_SIZE 
    
    if DEBUG:
        print "size of file is: " , sizeOfFile
        print "size of buffer is: ", BUFFER_SIZE
        print "Number of needed iterations is", recvCount

    sumDataSize = sys.getsizeof(data)
    
    while (sys.getsizeof(data) < sizeOfFile):
        data += s.recv(BUFFER_SIZE)


s.close()
f = open ('/Users/tylerfetters/Desktop/CS594/Project3/Project3/Project3/'+fName , 'w')
f.write (data)

