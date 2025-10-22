from socket import *
import os
import sys
import struct
import time
import select
import binascii

ICMP_ECHO_REQUEST = 8

def checksum(source: bytes) -> int:
    csum = 0
    countTo = (len(source) // 2) * 2
    count = 0

    while count < countTo:
        thisVal = source[count + 1] * 256 + source[count]
        csum = csum + thisVal
        csum = csum & 0xffffffff
        count = count + 2

    if countTo < len(source):
        csum = csum + source[len(source) - 1]
        csum = csum & 0xffffffff

    csum = (csum >> 16) + (csum & 0xffff)
    csum = csum + (csum >> 16)
    answer = ~csum
    answer = answer & 0xffff
    # swap bytes
    answer = answer >> 8 | ((answer & 0xff) << 8)
    return answer

def receiveOnePing(mySocket, ID, timeout, destAddr):
    timeLeft = timeout

    while 1:
        startedSelect = time.time()
        whatReady = select.select([mySocket], [], [], timeLeft)
        howLongInSelect = (time.time() - startedSelect)

        if whatReady[0] == []: # Timeout
            return "Request timed out."

        timeReceived = time.time()
        recPacket, addr = mySocket.recvfrom(1024)

        # Fill in start
        # Determine IP header length from first byte (IHL)
        first_byte = recPacket[0]
        ihl = first_byte & 0x0F
        ip_header_len = ihl * 4

        # Extract ICMP header and ensure we have enough bytes
        icmp_header = recPacket[ip_header_len: ip_header_len + 8]
        if len(icmp_header) < 8:
            # malformed/short packet; continue waiting
            timeLeft = timeLeft - howLongInSelect
            if timeLeft <= 0:
                return "Request timed out."
            continue

        # Unpack ICMP header as unsigned bytes/shorts (network order not needed here
        # because we're unpacking from bytes; use '!' to be explicit)
        icmp_type, icmp_code, icmp_checksum, icmp_id, icmp_seq = struct.unpack("!BBHHH", icmp_header)

        # Only accept Echo Reply (type 0) with matching ID
        if icmp_type == 0 and icmp_id == ID:
            # extract the timestamp (double) placed in the ICMP payload by sendOnePing
            data_offset = ip_header_len + 8
            time_struct_size = struct.calcsize("!d")
            if len(recPacket) >= data_offset + time_struct_size:
                timeSent = struct.unpack("!d", recPacket[data_offset:data_offset + time_struct_size])[0]
                delay = timeReceived - timeSent
                return delay
            else:
                return "Reply received (no timestamp)."
        # If not the reply we want, keep waiting
        # Fill in end

        timeLeft = timeLeft - howLongInSelect
        if timeLeft <= 0:

            return "Request timed out."

def sendOnePing(mySocket, destAddr, ID):
    # Header is type (8), code (8), checksum (16), id (16), sequence (16)
    myChecksum = 0

    # Make a dummy header with a 0 checksum
    # pack header and timestamp in network order explicitly
    header = struct.pack("!BBHHH", ICMP_ECHO_REQUEST, 0, myChecksum, ID, 1)
    data = struct.pack("!d", time.time())

    # Compute checksum over the raw bytes
    myChecksum = checksum(header + data)

    # Put checksum into the header (network order)
    header = struct.pack("!BBHHH", ICMP_ECHO_REQUEST, 0, myChecksum, ID, 1)
    packet = header + data

    mySocket.sendto(packet, (destAddr, 1)) # AF_INET address must be tuple, not str

# Both LISTS and TUPLES consist of a number of objects
# which can be referenced by their position number within the object.

def doOnePing(destAddr, timeout):
    icmp = getprotobyname("icmp")

    # SOCK_RAW is a powerful socket type. For more details:   http://sock-
    # raw.org/papers/sock_raw
    mySocket = socket(AF_INET, SOCK_RAW, icmp)
    myID = os.getpid() & 0xFFFF  # Return the current process i

    sendOnePing(mySocket, destAddr, myID)
    delay = receiveOnePing(mySocket, myID, timeout, destAddr)

    mySocket.close()

    return delay

def ping(host, timeout=1):
    # timeout=1 means: If one second goes by without a reply from the server,
    # the client assumes that either the client's ping or the server's pong is lost
    dest = gethostbyname(host)

    print("Pinging " + host + " @ address: " + dest + " using ICMP pinger:")
    print("")

    # Send ping requests to a server separated by approximately one second
    while 1 :
        delay = doOnePing(dest, timeout)
        print(delay)
        time.sleep(1)# one second
    return delay

ping("google.com")
