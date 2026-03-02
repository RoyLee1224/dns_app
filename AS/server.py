import socket
import os

UDP_IP = "0.0.0.0"
UDP_PORT = 53533 
DB_FILE = "dns_records.txt"

def start_as():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((UDP_IP, UDP_PORT))
    print(f"Authoritative Server (AS) is running on UDP port {UDP_PORT}...")

    while True:
        data, addr = sock.recvfrom(1024)
        message = data.decode('utf-8')
        lines = message.strip().split('\n')
        
        dns_info = {}
        for line in lines:
            if '=' in line:
                key, value = line.split('=', 1)
                dns_info[key.strip()] = value.strip()

        if 'VALUE' in dns_info:
            name = dns_info.get('NAME')
            value = dns_info.get('VALUE')
            if name and value:
                with open(DB_FILE, "a") as f:
                    f.write(f"{name},{value}\n")
                print(f"Registered: {name} -> {value}")
        
        else:
            query_name = dns_info.get('NAME')
            found_ip = None
            
            if os.path.exists(DB_FILE):
                with open(DB_FILE, "r") as f:
                    for line in f:
                        name, ip = line.strip().split(',')
                        if name == query_name:
                            found_ip = ip
            
            if found_ip:
                response = f"TYPE=A\nNAME={query_name}\nVALUE={found_ip}\nTTL=10\n"
                sock.sendto(response.encode('utf-8'), addr)
                print(f"Queried: {query_name}, Replied with IP: {found_ip}")

if __name__ == '__main__':
    start_as()