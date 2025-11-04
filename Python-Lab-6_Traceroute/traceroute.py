from socket import *
import os
import sys
import struct
import time
import select

ICMP_ECHO_REQUEST = 8
MAX_HOPS = 30
TIMEOUT = 2.0
TRIES = 2


def checksum(source_bytes):
    """
    helper to compute the Internet Checksum of the supplied data.
    """
    count_to = (len(source_bytes) // 2) * 2
    chksum = 0
    count = 0

    # Handle bytes in pairs (16 bits)
    while count < count_to:
        this_val = source_bytes[count + 1] * 256 + source_bytes[count]
        chksum = chksum + this_val
        chksum = chksum & 0xffffffff
        count += 2

    # Handle last byte if present (odd-length)
    if count_to < len(source_bytes):
        chksum = chksum + source_bytes[len(source_bytes) - 1]
        chksum = chksum & 0xffffffff

    # Fold 32-bit sum to 16 bits
    chksum = (chksum >> 16) + (chksum & 0xffff)
    chksum = chksum + (chksum >> 16)
    answer = ~chksum
    answer = answer & 0xffff
    # Swap bytes
    answer = answer >> 8 | (answer << 8 & 0xff00)
    return answer


def build_packet():
    """
    helper to build an ICMP Echo Request packet with current time as data.
    1. Create header with checksum = 0
    2. Append data (timestamp)
    3. Recalculate checksum over header+data
    4. Rebuild header with correct checksum
    """
    my_id = os.getpid() & 0xFFFF  # Return the current process id
    my_seq = 1

    # ICMP Header: Type (8), Code (0), Checksum (0), ID, Sequence
    header = struct.pack("bbHHh", ICMP_ECHO_REQUEST, 0, 0, my_id, my_seq)
    data = struct.pack("d", time.time())

    # Calculate checksum on the header and data
    my_checksum = checksum(header + data)

    # Repack header with correct checksum (network byte order)
    header = struct.pack("bbHHh", ICMP_ECHO_REQUEST, 0, htons(my_checksum), my_id, my_seq)

    packet = header + data
    return packet


def get_route(hostname):
    time_left = TIMEOUT

    for ttl in range(1, MAX_HOPS + 1):
        for tries in range(TRIES):
            dest_addr = gethostbyname(hostname)

            # Fill in start
            # Make a raw socket named mySocket
            mySocket = socket(AF_INET, SOCK_RAW, IPPROTO_ICMP)
            # Fill in end

            # Set TTL on the socket
            mySocket.setsockopt(IPPROTO_IP, IP_TTL, struct.pack('I', ttl))
            mySocket.settimeout(TIMEOUT)

            try:
                packet = build_packet()
                send_time = time.time()
                mySocket.sendto(packet, (dest_addr, 0))

                started_select = time.time()
                what_ready = select.select([mySocket], [], [], time_left)
                how_long_in_select = (time.time() - started_select)

                if what_ready[0] == []:  # Timeout
                    print("  *        *        *    Request timed out.")
                    continue

                recv_packet, addr = mySocket.recvfrom(1024)
                time_received = time.time()
                time_left = time_left - how_long_in_select
                if time_left <= 0:
                    print("  *        *        *    Request timed out.")
                    continue

            except timeout:
                # If we hit a socket timeout, try again
                continue

            else:
                # Fill in start
                # Fetch the ICMP type from the IP packet
                # IP header is 20 bytes; ICMP header starts at byte 20
                icmp_header = recv_packet[20:28]
                types, code, chksum, p_id, sequence = struct.unpack("bbHHh", icmp_header)
                # Fill in end

                if types == 11:  # Time Exceeded

                    bytes_in_double = struct.calcsize("d")
                    time_sent = struct.unpack("d", recv_packet[28:28 + bytes_in_double])[0]
                    print("  %d    rtt=%.0f ms    %s" %
                          (ttl, (time_received - send_time) * 1000, addr[0]))

                elif types == 3:  # Destination Unreachable
                    bytes_in_double = struct.calcsize("d")

                    print("  %d    rtt=%.0f ms    %s" %
                          (ttl, (time_received - send_time) * 1000, addr[0]))

                elif types == 0:  # Echo Reply – reached destination
                    bytes_in_double = struct.calcsize("d")
                    time_sent = struct.unpack("d", recv_packet[28:28 + bytes_in_double])[0]
                    print("  %d    rtt=%.0f ms    %s" %
                          (ttl, (time_received - time_sent) * 1000, addr[0]))
                    return
                else:
                    print("error")
                    break

            finally:
                mySocket.close()


if __name__ == "__main__":
    host = "ucumberlands.edu"
    dest = gethostbyname(host)

    print("--- Pinging " + host + " @ address: " + dest + "")

    get_route(host)
