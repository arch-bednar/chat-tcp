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
            if data == "#?whoareyou?#":
                name=input("Enter your name: ")
                name = name + f"<ID: {str(self.s.fileno())}"
                self.s.send(name.encode())
            elif data.startswith("#?PVTFROM?#"):

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

    def sendToOneClient(self, id):
        for client in self.client_list:
            if client.id == id:
                return id
        return -1

    def cutUserId(self, data):
        index = data.find("#!SENDTO#")
        seq = data[len("#!SENDTO#"):]
        if not seq.startswith("<"):
            raise Exception("Command #!SENDTO# has be occurred with '<user_id>'")
        close_bracket_index = seq.find(">")
        if close_bracket_index == -1:
            raise Exception("There is no close bracket '>' at command")
        id = seq[1:close_bracket_index]
        return id

    def returnListOfUsers(self):
        list=str()
        counter=0
        for client in self.client_list:
            list += client.name + "<"+client.id+">"+chr(10)
            counter+=1

        list = f"Total {counter} online."+chr(10)+list
        return list.encode()

    def handleClient(self, conn, addr):
        with conn:
            conn.send(b"#?whoareyou?#")
            data = bytes
            data = conn.recv(1024)
            conn.sendall(b"")
            while True:
                data = conn.recv(1024)
                if not data: #connection broken
                    break
                elif data == "#?LIST?#": #listing all users
                    conn.send(self.returnListOfUsers())
                elif data.startswith("#?SENDTO?#"): #sending private message
                    try:
                        id=self.cutUserId(data)
                    except Exception as e:
                        print(e)

                    client_id = self.sendToOneClient(id)
                    if client_id == -1: #checks if client exists
                        raise Exception(f"There is no user with id={id}")
                    else:
                        for client in self.client_list:
                            if client.id == client_id:
                                client.socket.send((f"Whisper<{conn.fileno()}>:"+data[data.find(">"):]).encode())
                else: #sends message to all users
                    conn.sendall(data)

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

    def checkClientId(self, client_socket):
        for client in self.client_list:
            if client.id == client_socket.fileno():
                return 1
        return 0

    def main(self):
        self.s.listen()
        while True:
            conn, addr=self.s.accept()
            client_thread = threading.Thread(target=self.handleClient, args=(conn, addr))
            client_thread.start()


# def clientPart(conn, addr):
#     with conn:
#         conn.send(b"#?whoareyou?")
#         data = conn.recv(1024)
#         while True:
#             data = conn.recv(1024)
#             if not data:
#                 break
#             print(f"{data}")

if __name__ == "__main__":
    pass