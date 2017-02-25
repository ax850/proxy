import socket, sys,requests
from thread import *

host = ''
port = sys.argv[1] #8000

print("Waiting for connection...")

def get_host(buffer):
    end = buffer.find('\n')
    host_request = buffer[:end].split()[1]
    check = host_request.split("/")[1]
    type = host_request.split("/")[-1].lower()
    host = host_request.rsplit("/", 1)[0]
    host = host.replace("/proxy/", "")
    host = host.replace("http://", "")  # Finding the URL host
    return host, check, type

def get_form(buffer):
    buf = buffer.rsplit('\n', 1)[1]
    buf = buf.replace(",", " ")
    list = buf.split()
    dic = {}
    for entry in list:
        key, val = entry.split('=')
        dic[key] = str(val)
    return dic

def threaded_client(conn):
    while True:
        buffer_ = conn.recv(4096) # Recieves the cURL
        host_,check,type_ = get_host(buffer_)
        reply = ""
        if check == "proxy":
            if type_ == "get":
                response = requests.get('http://'+host_+'/get')
                reply = response.text
            elif type_ == "post":  #post
                dic = get_form(buffer_) # convert form to dict type
                response = requests.post('http://' + host_ + '/post', data = dic)
                reply = response.text
        elif check != "proxy":
            conn.close()
        print('Recieving Data From Server...')
        if not reply:
            break
        conn.send(str(reply.encode('utf-8'))) # encode to utf-8

while True:
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR,1)
    try:
        s.bind((host, int(port)))
    except socket.error as e:
        print(str(e))
    s.listen(5)  # Basically a que, number of incoming connections at a time
    conn, addr = s.accept()
    print('connected to:' + addr[0] + ':' + str(addr[1]))
    start_new_thread(threaded_client, (conn,))
