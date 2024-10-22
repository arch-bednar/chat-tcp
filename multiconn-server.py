import threading
import socket
import user
class Server:
    def __init__(self, HOST="127.0.0.1"):
        self.client_list = []
        self.HOST = HOST
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    ##binds socket to port
    def bindTo(self):
        free_port = self.get_free_port(self.socket, self.HOST)
        if free_port == -1:
            raise RuntimeError("Failure to bind socket to free port! No free port available!")
        print(f"Server bound to port: {free_port}")

    def _sendToOneClient(self, id, text):
        for client in self.client_list:
            print("client id:" + str(client.id) + " " + str(id))
            if str(client.id) == id:
                client.socket.send(text.encode())
                return None
        return "There is no such a host"

    def cutUserId(self, data):
        index = data.find("MESG ")
        seq = data[len("MESG "):]
        seq.split(" ")
        return seq[0]

    def returnListOfUsers(self):
        list=str()
        counter=0
        for client in self.client_list:
            list += client.name + "<"+str(client.id)+">"+chr(10)
            counter += 1

        list = f"Total {counter} online."+chr(10)+list
        return list.encode()

    def sendToAll(self, data, id):
        print("sendToAll")
        fromUser = self._getClientInfo(id) + ": "
        for client in self.client_list:
            if client.id == id:
                #print("sameClient")
                continue
            else:
                #print("send to other client")
                client.socket.send((fromUser + data).encode())

    def _getClientInfo(self, id):
        for user in self.client_list:
            if user.id == id:
                return str(user)
        return "No a such user"

    def _removeClient(self, id):
        for client in self.client_list:
            if client.id == id:
                self.client_list.remove(client)

    def handleClient(self, conn, addr):
        with conn:
            conn.send(b"Who are you?")
            data = bytes
            data = conn.recv(1024)
            data = data.decode("utf-8")
            self.addNewClient(conn, data)
            #conn.sendall(b"")
            self.sendToAll(f"User {self._getClientInfo(conn.fileno())} is online now", conn.fileno())
            handlingClient = True
            while handlingClient:
                try:
                    data = conn.recv(1024)
                    data = data.decode("utf-8")
                    if not data: #connection is broken
                        break
                    elif data.startswith("LIST"): #listing all users
                        conn.send(self.returnListOfUsers())
                    elif data.startswith("QUIT"):
                        #conn.sendall(f"User {self._getClientInfo(conn.fileno())} has been disconnected".encode())
                        self.sendToAll(f"User {self._getClientInfo(conn.fileno())} has been disconnected", conn.fileno())
                        self._removeClient(conn.fileno())
                    elif data.startswith("MESG "):
                        args = data.split(" ")
                        if len(args) < 3:
                            conn.send(f"Not enough arguments: required 3, but {len(args)} were given!".encode())
                        else:
                            x = self._sendToOneClient(args[1], f"{self._getClientInfo(conn.fileno())} whispers: " + chr(32).join(args[2:]))
                            if not x is None:
                                conn.send(x.encode())
                    else: #sends message to all users
                        self.sendToAll(data, conn.fileno())
                        print(f"{data}")
                except ConnectionResetError:
                    self.sendToAll(f"User {conn.fileno()} disconnected", conn.fileno())
                    handlingClient = False
                    self._removeClient(conn.fileno())
                except KeyboardInterrupt:
                    self.sendToAll(f"Server is down...", -1)
                except Exception as e:
                    print(e)

    def get_free_port(self, sock, address):
        for i in range(40000, 60001):
            try:
                sock.bind((address, i))
                return i
            except OSError:
                continue
        return -1

    def addNewClient(self, socket, name):
        newUser = user.user(socket, name)
        self.client_list.append(newUser)

    def checkClientId(self, client_socket):
        for client in self.client_list:
            if client.id == client_socket.id:
                return 1
        return 0

    def start(self):
        self.bindTo()
        self.socket.listen()
        client_thread = None
        isRunning = True
        while isRunning:
            try:
                conn, addr = self.socket.accept()
                print(f"New client connected! {conn.fileno()}")
                client_thread = threading.Thread(target=self.handleClient, args=(conn, addr))
                client_thread.start()
            except KeyboardInterrupt:
                isRunning = False
                client_thread.join(1000)



if __name__ == "__main__":
    server = Server("127.0.0.1")
    server.start()