import socket
import threading


class Client:
    def __init__(self, HOST="127.0.0.1"):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.HOST = HOST
        self.name = ""
        self.id = 0

    def getListetnigPort(self, socket, address):
        for port in range(40000, 60001):
            try:
                socket.connect((address, port))
                return port
            except OSError:
                continue
        return -1

    def main(self):
        lst_port = self.getListetnigPort(self.socket, self.HOST)

        if lst_port == -1:
            raise RuntimeError("There is no listening port!")

        while True:
            data = self.s.recv(1024)
            if data == "#?whoareyou#":
                name=input("Enter your name: ")
                name = name + f"<ID: {str(self.s.fileno())}"
                self.s.send(name.encode())
            else:
                print(data)



class Server:
    def __init__(self, HOST="127.0.0.1"):
        self.client_list = []
        self.HOST = HOST
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def bindTo(self, address):
        free_port = self.get_free_port(self.socket, self.HOST)
        if free_port == -1:
            raise RuntimeError("Failure to bind socket to free port! No free port available!")

    def handleClient(self, conn, addr):
        with conn:
            conn.send(b"#?whoareyou?")
            data = conn.recv(1024)
            conn.sendall(b"")
            while True:
                data = conn.recv(1024)
                if not data:
                    break
                print(f"{data}")

    def get_free_port(sock, address):
        for i in range(40000, 60001):
            try:
                sock.bind((address, i))
                return i
            except OSError:
                continue
        return -1

    def addNewClient(self, socket):
        self.client_list.append(socket)

    def main(self):
        self.s.listen()
        while True:
            conn, addr = s.accept()
            client_thread = threading.Thread(target=self.handleClient, args=(conn, addr))
            client_thread.start()



def clientPart(conn, addr):
    with conn:
        conn.send(b"#?whoareyou?")
        data = conn.recv(1024)
        while True:
            data = conn.recv(1024)
            if not data:
                break
            print(f"{data}")

if __name__ == "__main__":
