import socket
import sys

# Create TCP welcoming socket
serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Prepare a server socket
serverPort = 6789
serverSocket.bind(('', serverPort))  # bind to all available interfaces
serverSocket.listen(1)  # maximum 1 connection in the queue

while True:
    # Establish the connection
    print('Ready to serve...')
    connectionSocket, addr = serverSocket.accept()

    try:
        message = connectionSocket.recv(1024).decode()  # receive request message
        message_parts = message.split()
        if len(message_parts) < 2:
            raise IOError("Invalid HTTP request")
        filename = message_parts[1]  # extract filename
        f = open(filename[1:])  # remove '/' from file path
        outputdata = f.read()

        # Send one HTTP header line into socket
        connectionSocket.send("HTTP/1.1 200 OK\r\n\r\n".encode())

        # Send the content of the requested file to the client
        for i in range(0, len(outputdata)):
            connectionSocket.send(outputdata[i].encode())
        connectionSocket.send("\r\n".encode())

        connectionSocket.close()

    except IOError:
        # Send response message for file not found
        connectionSocket.send("HTTP/1.1 404 Not Found\r\n\r\n".encode())
        connectionSocket.send("<html><body><h1>404 Not Found</h1></body></html>\r\n".encode())

        # Close client socket
        connectionSocket.close()

serverSocket.close()
sys.exit()  # Terminate the program after sending the corresponding data
