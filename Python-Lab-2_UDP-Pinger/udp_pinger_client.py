import time
from socket import *

# Server details
serverName = '127.0.0.1'   # localhost
serverPort = 12000

# Create UDP client socket
clientSocket = socket(AF_INET, SOCK_DGRAM)
clientSocket.settimeout(1)   # 1 second timeout

# Send 10 pings
for sequence_number in range(1, 11):
    # Record send time
    sendTime = time.time()
    message = f"Ping {sequence_number} {sendTime}"

    try:
        # Send ping to server
        clientSocket.sendto(message.encode(), (serverName, serverPort))

        # Wait for reply
        modifiedMessage, serverAddress = clientSocket.recvfrom(1024)
        recvTime = time.time()

        # Calculate Round Trip Time - RTT
        rtt = recvTime - sendTime

        print(f"Reply from {serverAddress}: {modifiedMessage.decode()}; round trip time (RTT) = {rtt:.6f} sec")

    except timeout:
        print("Request timed out")

# Close socket
clientSocket.close()
