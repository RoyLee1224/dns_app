from flask import Flask, request
import socket

app = Flask(__name__)

def fibonacci(n):
    if n < 0:
        raise ValueError
    if n == 0:
        return 0
    elif n == 1:
        return 1
    a, b = 0, 1
    for _ in range(2, n + 1):
        a, b = b, a + b
    return b

@app.route('/register', methods=['PUT'])
def register():
    data = request.get_json()
    if not data:
        return "Bad Request", 400
    
    hostname = data.get('hostname')
    ip = data.get('ip')
    as_ip = data.get('as_ip')
    as_port = data.get('as_port')

    if not all([hostname, ip, as_ip, as_port]):
        return "Missing parameters", 400

    dns_message = f"TYPE=A\nNAME={hostname}\nVALUE={ip}\nTTL=10\n"
    
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.sendto(dns_message.encode('utf-8'), (as_ip, int(as_port)))
        sock.close()
        return "Registered Successfully", 201
    except Exception as e:
        return str(e), 500

@app.route('/fibonacci', methods=['GET'])
def get_fibonacci():
    number_str = request.args.get('number')
    if number_str is None:
        return "Bad format", 400
    
    try:
        x = int(number_str)
        result = fibonacci(x)
        return str(result), 200
    except ValueError:
        return "Bad format", 400

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=9090)