from socket import *

# Message to send
msg = "\r\nI love computer networks!"
endmsg = "\r\n.\r\n"

# Local test SMTP server (DebuggingServer)
mailserver = ("localhost", 1025)

# Create socket and connect to the local server
clientSocket = socket(AF_INET, SOCK_STREAM)
clientSocket.connect(mailserver)

recv = clientSocket.recv(1024).decode()
print("S:", recv)
if recv[:3] != '220':
    print("220 reply not received from server.")

# Send HELO command and print server response.
heloCommand = "HELO Alice\r\n"
clientSocket.send(heloCommand.encode())
recv1 = clientSocket.recv(1024).decode()
print("S:", recv1)
if recv1[:3] != '250':
    print("250 reply not received from server.")

# Send MAIL FROM command and print server response.
mailFrom = "MAIL FROM:<sender@test.com>\r\n"
clientSocket.send(mailFrom.encode())
recv2 = clientSocket.recv(1024).decode()
print("S:", recv2)

# Send RCPT TO command and print server response.
rcptTo = "RCPT TO:<receiver@test.com>\r\n"
clientSocket.send(rcptTo.encode())
recv3 = clientSocket.recv(1024).decode()
print("S:", recv3)

# Send DATA command and print server response.
data = "DATA\r\n"
clientSocket.send(data.encode())
recv4 = clientSocket.recv(1024).decode()
print("S:", recv4)

# Send message data.
clientSocket.send(msg.encode())

# Message ends with a single period.
clientSocket.send(endmsg.encode())
recv5 = clientSocket.recv(1024).decode()
print("S:", recv5)

# Send QUIT command and get server response.
quitCmd = "QUIT\r\n"
clientSocket.send(quitCmd.encode())
recv6 = clientSocket.recv(1024).decode()
print("S:", recv6)

# Close socket
clientSocket.close()
