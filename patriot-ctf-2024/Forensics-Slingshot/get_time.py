import pyshark

def get_timestamp_of_packet(pcap_file, packet_number=0):
    # Open the capture file
    capture = pyshark.FileCapture(pcap_file)

    # Retrieve the timestamp from the packet of interest
    packet = capture[packet_number]  # Access the first packet or whichever one contains the encrypted data
    timestamp = float(packet.sniff_time.timestamp())

    capture.close()
    return timestamp

def main():
    pcap_file = 'Slingshot.pcapng'  # Your pcapng file
    packet_number = 13217  # Change this to the correct packet index that contains the encrypted data

    # Get the timestamp
    timestamp = get_timestamp_of_packet(pcap_file, packet_number)
    print(f"Timestamp of the packet: {timestamp} (UNIX time)")

if __name__ == '__main__':
    main()

