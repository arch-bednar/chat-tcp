import socket
import threading


class Client:
    def __init__(self, HOST="127.0.0.1"):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.HOST = HOST
        self.name = ""
        self.id = 0

    def __getListetnigPort(self, socket, address):
        print("__getListetnigPort")
        for port in range(40000, 60001):
            try:
                socket.connect((address, port))
                return port
            except OSError:
                continue
        return -1

    def __listen(self):
        while True:
            print("Listening...")
            data = self.socket.recv(1024)
            if not data:
                continue
            print(data)

    def main(self):
        print("main")
        lst_port = self.__getListetnigPort(self.socket, self.HOST)

        if lst_port == -1:
            raise RuntimeError("There is no listening port!")

        data = self.socket.recv(1024)
        print(data)

        line = input("> ")
        self.socket.sendall(line.encode())

        threading.Thread(target=self.__listen).start()
        print("petla")
        while True:
            line = input("> ")
            if len(line) == 0:
                continue
            self.socket.sendall(line.encode())
            #data = self.socket.recv(1024)
            # if data == "#?whoareyou?#":
            #     name=input("Enter your name: ")
            #     name = name + f"<ID: {str(self.s.fileno())}"
            #     self.s.send(name.encode())
            # elif data.startswith("#?PVTFROM?#"):
            #     pass
            # else:
            #     print(data)
            #print(data)


if __name__ == "__main__":
    client = Client("127.0.0.1")
    client.main()