from socket import *
import sys
import os

if len(sys.argv) <= 1:
    print('Usage: "python ProxyServer.py server_ip"\n[server_ip : It is the IP Address Of Proxy Server]')
    sys.exit(2)

# Create a server socket, bind it to a port and start listening
tcpSerSock = socket(AF_INET, SOCK_STREAM)

# Fill in start.
server_ip = sys.argv[1]          # e.g. 127.0.0.1
server_port = 8888               # you can change this if you like
tcpSerSock.bind((server_ip, server_port))
tcpSerSock.listen(5)
# Fill in end.

while True:
    # Start receiving data from the client
    print('Ready to serve...')
    tcpCliSock, addr = tcpSerSock.accept()
    print('Received a connection from:', addr)

    # Fill in start.
    message = tcpCliSock.recv(4096).decode()
    # Fill in end.

    # If the client sent nothing, just close and wait for next
    if not message:
        tcpCliSock.close()
        continue

    print(message)

    # Extract the filename from the given message
    try:
        first_line = message.split()
        # e.g. GET /www.google.com HTTP/1.1
        filename = first_line[1].partition("/")[2]
    except Exception:
        tcpCliSock.close()
        continue

    print("Requested filename:", filename)

    fileExist = "false"
    filetouse = "/" + filename
    print("File to use (cache path):", filetouse)

    try:
        # Check whether the file exists in the cache
        f = open(filetouse[1:], "rb")  # open from current dir
        outputdata = f.read()
        fileExist = "true"

        # ProxyServer finds a cache hit and generates a response message
        # Note: send bytes in Python 3
        tcpCliSock.send(b"HTTP/1.0 200 OK\r\n")
        tcpCliSock.send(b"Content-Type: text/html\r\n")
        # Fill in start.
        tcpCliSock.send(b"\r\n")          # end of headers
        tcpCliSock.sendall(outputdata)    # send cached content
        # Fill in end.
        print('Read from cache')
        f.close()

    except IOError:
        # File not found in cache
        if fileExist == "false":
            # Create a socket on the proxy server
            # Fill in start.
            c = socket(AF_INET, SOCK_STREAM)
            # Fill in end.

            # Some URLs begin with "www." – original lab strips it:
            hostn = filename.replace("www.", "", 1)
            print("Host to contact:", hostn)

            try:
                # Connect to the socket to port 80
                # Fill in start.
                c.connect((hostn, 80))
                # Fill in end.

                # Create a temporary file on this socket and ask port 80 for the file
                fileobj = c.makefile('rwb', 0)

                # Send GET request to the origin server
                request_line = b"GET http://" + filename.encode() + b" HTTP/1.0\r\n\r\n"
                fileobj.write(request_line)

                # Read the response into buffer
                # Fill in start.
                response = b""
                while True:
                    data = c.recv(4096)
                    if not data:
                        break
                    response += data
                # Fill in end.

                # Create a new file in the cache for the requested file.
                # Also send the response in the buffer to client socket
                # and the corresponding file in the cache
                # NOTE: make sure directory exists
                cache_path = "./" + filename
                # Create intermediate dirs if needed
                os.makedirs(os.path.dirname(cache_path), exist_ok=True)

                tmpFile = open(cache_path, "wb")
                # Fill in start.
                tmpFile.write(response)
                tmpFile.close()
                tcpCliSock.sendall(response)
                # Fill in end.

            except Exception as e:
                print("Illegal request or fetch failed:", e)
                # If we can’t get it from remote, send 404 to client
                # Fill in start.
                tcpCliSock.send(b"HTTP/1.0 404 Not Found\r\n")
                tcpCliSock.send(b"Content-Type: text/html\r\n\r\n")
                tcpCliSock.send(b"<html><body><h1>404 Not Found</h1></body></html>")
                # Fill in end.

        else:
            # HTTP response message for file not found
            # Fill in start.
            tcpCliSock.send(b"HTTP/1.0 404 Not Found\r\n")
            tcpCliSock.send(b"Content-Type: text/html\r\n\r\n")
            tcpCliSock.send(b"<html><body><h1>404 Not Found</h1></body></html>")
            # Fill in end.

    # Close the client socket
    tcpCliSock.close()

# Fill in start.
tcpSerSock.close()
# Fill in end.
