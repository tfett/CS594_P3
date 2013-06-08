#Ian Van Houdt
#CS 494

#proxy.py

#Proxy must:
#
#   -Listen on TCP Port specified by command line: (as in server.py)
#       - python proxy.py -p <port>
#
#   -Parse each request to extract server name (from 'Host:' header)
#    and the requested url path. You may assume the Host header will
#    always be present (client.py)
#
#   -Look up the IP addr for the given server (server we will be sending to)
#
#   -Initiate a TCP connection to the server's IP addr on port 80 (client.py)
#
#   -Copy HTTP request to the server (from client's request)
#
#   -Retreive HTTP response from the server, and forward it on to the client.
#    **Proxy must support responses larger than a few KBs, which require mult
#      calls to the sockets' recv() and send methods
#
#   -Finally, your proxy must keep a log of each HTTP request that it serves.
#    The log should be a text file, named 'log.txt' with each request
#    represented by one line in the file. (SERVER PATH IP)
#       -eg: http://www.example.com/index/html from 1.2.3.4:
#       = www.example.com /index.html 1.2.3.4



import socket
import os
import sys

DEBUG = False
fileN = ""

def client(url, TCP_IP):
    global fileN
    
    TCP_PORT = 80
    BUFFER_SIZE = 1024
    
    
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((TCP_IP, TCP_PORT))
    #Submit a valid HTTP 1.1 request for the desired URL
    MESSAGE = "GET " + fileN + " HTTP/1.1\r\n"
    MESSAGE += "Host: " + url + " \r\n\r\n"
    
    s.send(MESSAGE)
     
    #actual stuff got save to the file
    data = s.recv(BUFFER_SIZE)
    
    hSize = data.find("\r\n\r\n")+41
    header = data[:hSize]
    
    
    
    #check success
    if DEBUG:
        print data
    
    data = data[hSize:]
    fileSize = header.find("Content-Length: ") + 16
    sizeEnd = header[fileSize:].find("\n")
    
    sizeOfFile = header[fileSize:fileSize+sizeEnd]
    sizeOfFile = int(sizeOfFile)

    #test filesize stuff
    #statinfo = os.stat(fileN)
    #sizeOfFile = statinfo.st_size
    
    recvCount = sizeOfFile/BUFFER_SIZE
    
    if DEBUG:
        print "size of file is: " , sizeOfFile
        print "size of buffer is: ", BUFFER_SIZE
        print "Number of needed iterations is", recvCount
    
    sumDataSize = sys.getsizeof(data)
    
    while (sys.getsizeof(data) < sizeOfFile):
      data += s.recv(BUFFER_SIZE)

    s.close()



    #Else, write standard
    varLen = fileN.rfind("/")
    fileN = fileN[varLen+1:]
    #print fileN
    data = header + data
    #print "Data: ", data
    f = open (fileN, "wb")
    f.write (data)
    f.close()


#Bring in command line args
port = sys.argv[2] #port number to listen on
port = int(port)


#Set IP and PORT to listen on:
TCP_IP = '127.0.0.1' # localhost
TCP_PORT = port  
BUFFER_SIZE = 1024


#Bind ports and listen
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind((TCP_IP, TCP_PORT))
s.listen(1) #max number of queued connections


#loop to continue recieving messages
while 1:
  conn, addr = s.accept()
  
  while 1:
      
    #Bring in data ****Must be able to recieve larger files than Buffer (see client.py)
    data = conn.recv(BUFFER_SIZE)

    #Test for successful reception
    if not data:
      break



    #Get header
    hSize = data.find("\r\n\r\n")+41
    header = data[:hSize]
    if DEBUG:
      print "\nHeader:\n", header
    
    
    
    #Get requested fileName ****Edit
    fileEnd = header.find(" HTTP/1.1")
    url = header[4:fileEnd]


    #Get Host to send to
    #extract the hostname
    if (url[0:11] == "http://www."):
      url = url[11:]
    if (url[0:7] == "http://"):
      url = url[7:]
    if (url[0:3] == "www"):
      url = url[4:]



    locN = url.find("/")
    if (locN != -1):
      fileN = url[locN:]
      url = url[:locN]
    else:
      fileN = url[locN:]
      url = url[:locN]
      
    if (fileN[-1] == "/"):
      fileN = fileN + "index.html"

    #DNS lookup to retrieve the IP address for the server using
    TCP_IP = socket.gethostbyname(url)

    ###LOG url, fileN, TCP_IP into log.txt
    f = open('log.txt', "a")
    logEntry = url + " " + fileN + " " + TCP_IP + "\n"
    f.write(logEntry)
    f.close()


    ###call client(url ,fileN, TCP_IP) to connect to server
    client(url, TCP_IP)


    ##response is written to file. read it into memory and send it to requester
    if DEBUG:
        print "FileName: ", fileN
    
    #Set path for directory and file
    path = fileN

    #See if file was written correctly
    if (os.path.exists(path)):
      if DEBUG:
        print "file exists"
      fileSize = os.path.getsize(path)
      fileSize = int(fileSize)
      

    #Send file. If bigger than Buffer, multiple sends
    if (fileSize <= BUFFER_SIZE):
      f = open(path, "rb")
      #data = f.read()
      conn.send(f.read())
    else:
      f = open(path, "rb")
      while (fileSize > 0):
        #data = f.read(BUFFER_SIZE)
        conn.send(f.read(BUFFER_SIZE))
        fileSize -= BUFFER_SIZE

    f.close()
    


  conn.close()
