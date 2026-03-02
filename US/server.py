from flask import Flask, request
import socket
import requests

app = Flask(__name__)

@app.route('/fibonacci', methods=['GET'])
def handle_fibonacci():
    hostname = request.args.get('hostname')
    fs_port = request.args.get('fs_port')
    number = request.args.get('number')
    as_ip = request.args.get('as_ip')
    as_port = request.args.get('as_port')

    if not all([hostname, fs_port, number, as_ip, as_port]):
        return "Bad Request: Missing parameters", 400

    dns_query = f"TYPE=A\nNAME={hostname}\n"
    fs_ip = None
    
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.settimeout(5.0)
        sock.sendto(dns_query.encode('utf-8'), (as_ip, int(as_port)))
        
        data, _ = sock.recvfrom(1024)
        response = data.decode('utf-8')
        sock.close()

        lines = response.strip().split('\n')
        for line in lines:
            if line.startswith('VALUE='):
                fs_ip = line.split('=')[1].strip()
                
    except Exception as e:
        return f"DNS Query Failed: {str(e)}", 500

    if not fs_ip:
        return "Could not resolve hostname from AS", 404

    try:
        fs_url = f"http://{fs_ip}:{fs_port}/fibonacci?number={number}"
        fs_response = requests.get(fs_url)
        
        if fs_response.status_code == 200:
            return fs_response.text, 200
        else:
            return fs_response.text, fs_response.status_code
            
    except Exception as e:
        return f"FS Request Failed: {str(e)}", 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)