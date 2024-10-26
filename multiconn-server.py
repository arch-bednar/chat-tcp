import threading
import socket
import time
import user
class Server:
    def __init__(self, HOST="127.0.0.1"):
        self._client_list = []
        self.HOST = HOST
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.stop_event = threading.Event()
        self.client_threads = []
        self._lock = threading.Lock()

    ##binds socket to port
    def bindTo(self):
        free_port = self.get_free_port(self.socket, self.HOST)
        if free_port == -1:
            raise RuntimeError("Failure to bind socket to free port! No free port available!")
        print(f"Server bound to port: {free_port}")

    def _sendToOneClient(self, sender, id, text):
        for client in self._client_list:
            #print("client id:" + client.id + " " + id)
            if str(client.id) == id:
                print(f"Sending private message from {sender} to {client.name}<{client.id}>")
                client.socket.send(text.encode())
                return None
        return "There is no such a host"

    # cuts user id from data
    def cutUserId(self, data):
        index = data.find("MESG ")
        seq = data[len("MESG "):]
        seq.split(" ")
        return seq[0]

    # returns list of users
    def returnListOfUsers(self):
        list=str()
        counter=0
        for client in self._client_list:
            list += client.name + "<"+client.id+">"+chr(10)
            counter += 1

        list = f"Total {counter} online."+chr(10)+list
        return list.encode()

    def sendToAll(self, data, id):
        print(f"User {id} sends message to all")
        fromUser = self._getClientInfo(id) + ": "
        for client in self._client_list:
            if client.id == id:
                #print("sameClient")
                continue
            else:
                #print("send to other client")
                client.socket.send((fromUser + data).encode())

    def _getClientInfo(self, id):
        #print(type(id))
        if type(id) is str:
            for user in self._client_list:
                if user.id == id:
                    return str(user)
        return "No a such user"

    def _getClientInfoBySocket(self, sock):
        #print("_getClientInfoBySocket: " + str(type(sock) is socket.socket))
        #print("if socket socket")
        for user in self._client_list:
            #print(str(id(user.socket)) + " " + str(id(sock)))
            if user.socket == sock:
                return user.name + f"<{user.id}>"

    def _getClientId(self, sock):
        #print("_getClientId")
        for user in self._client_list:
            if user.socket == sock:
                #print(str(id(user.socket)) + " " + str(id(sock)))
                return user.id
        return -1

    def addNewClient(self, socket, name, id):
        newUser = user.user(socket, name, id)
        self._client_list.append(newUser)

    def _checkClientData(self, data):
        lbracket = data.find("<")
        rbracket = data.find(">")
        spcboard = data.find(chr(10))

        if spcboard > -1:
            return "No space board allowed!"
        elif lbracket == 0:
            return "There is no name given before brackets"
        elif lbracket - rbracket > 0:
            return "Expected '<', but '>' found"
        elif lbracket - rbracket == -1:
            return "There is no id between <>"

        name = data[:data.find("<")]
        id = data[data.find("<")+1:data.find(">")]

        nameCheck = self._checkClientName(name)
        if nameCheck != "OK":
            return nameCheck

        idCheck = self._checkClientId(id)
        if idCheck != "OK":
            return idCheck

        return "OK"


    #returns: 1-then illegal character (not from 0-9, a-z or A-Z), 2 - wrong type, 0 - correct
    def _checkClientName(self, name):
        #print(name + " " + str(len(name)))
        if type(name) != str:
            return "Wrong type of name"

        for i in name:
            letter = ord(i)
            if letter in range(48,58) or letter in range(65,91) or letter in range(97, 123):
                continue
            else:
                return "Name contains illegal characters"

        for client in self._client_list:
            if client.name == name:
                return "That user name already exists"

        return "OK"

    # returns: 1-then illegal character (not from 0-9, a-z or A-Z), 2 - wrong type, 3-wrong length, 0 - correct
    def _checkClientId(self, id):
        print(id)
        if type(id) != str:
            return "Wrong type of name"
        if len(id) != 8:
            return "Length of ID is not 8"

        for i in id:
            digit = ord(i)
            if digit in range(48, 58) or digit in range(65, 91) or digit in range(97, 123):
                continue
            else:
                return "Id contains illegal characters"

        for client in self._client_list:
            if client.id == id:
                return "That id is reserved by another user"
        return "OK"

    def _addClient(self, conn, data):
        print("add client")
        self._lock.acquire()
        print("lock")
        msg = self._checkClientData(data)
        if msg == "OK":
            self._client_list.append(user.user(conn, data[:data.find("<")], data[data.find("<")+1:data.find(">")]))
        self._lock.release()
        return msg

    def _removeClient(self, sock):
        for client in self._client_list:
            if client.socket == sock:
                self._client_list.remove(client)

    def handleClient(self, conn, addr, stop_event):
        #self.addNewClient(conn)
        with conn:
            conn.setblocking(False)
            conn.send(b"Who are you?")
            data = bytes
            data_received = False
            while not data_received and not stop_event.is_set():
                try:
                    data = conn.recv(1024)
                    if data:
                        data = data.decode("utf-8")
                        result = self._addClient(conn, data)
                        if  result == "OK":
                            #conn.sendall(b"")
                            id = data[data.find("<")+1:data.find(">")]
                            print(id)
                            self.sendToAll(f"User {data} is online now", self._getClientId(conn))
                            data_received = True
                            conn.sendall(result.encode())
                        else:
                            conn.sendall(result.encode())
                except BlockingIOError:
                    time.sleep(0.1)
                    continue
            print(f"{data} joins chat group! From " + addr[0])
            handlingClient = True
            while handlingClient and not stop_event.is_set():
                try:
                    data = conn.recv(1024)
                    data = data.decode("utf-8")
                    if not data: #connection is broken
                        break
                    elif data.startswith("LIST"): #listing all users
                        conn.send(self.returnListOfUsers())
                    elif data.startswith("QUIT"):
                        #conn.sendall(f"User {self._getClientInfo(conn.fileno())} has been disconnected".encode())
                        self.sendToAll(f"User {self._getClientInfoBySocket(conn)} has been disconnected", self._getClientId(conn))
                        self._removeClient(conn)
                    elif data.startswith("MESG "):
                        args = data.split(" ")
                        if len(args) < 3:
                            conn.send(f"Not enough arguments: required 3, but {len(args)} were given!".encode())
                        else:
                            sender = self._getClientInfoBySocket(conn)
                            x = self._sendToOneClient(sender, args[1], f"{sender} whispers: " + chr(32).join(args[2:]))
                            if not x is None:
                                conn.send(x.encode())
                    else: #sends message to all users
                        self.sendToAll(data, self._getClientId(conn))
                        print(f"{data}")
                except ConnectionResetError:
                    self.sendToAll(f"User {self._getClientInfoBySocket(conn)} disconnected",self._getClientId(conn))
                    handlingClient = False
                    self._removeClient(conn)
                except KeyboardInterrupt:
                    self.sendToAll(f"Server is down...", -1)
                except BlockingIOError:
                    time.sleep(0.1)
                    continue
                except Exception as e:
                    print(e)

    # finds free port for listening
    def get_free_port(self, sock, address):
        for i in range(40000, 60001):
            try:
                sock.bind((address, i))
                return i
            except OSError:
                continue
        return -1

    #returns 1 then client's id is in the list
    # def checkClientId(self, client_socket):
    #     for client in self._client_list:
    #         if client.id == client_socket.id:
    #             return 1
    #     return 0

    def start(self):
        self.bindTo()
        self.socket.listen()
        client_threads = []
        isRunning = True
        try:
            while isRunning:
                try:
                    conn, addr = self.socket.accept()
                    client_thread = threading.Thread(target=self.handleClient, args=(conn, addr, self.stop_event))
                    client_thread.start()
                except KeyboardInterrupt:
                    isRunning = False
                    self.stop_event.set()
        except Exception as e:
            print(e)
            self.socket.close()
            for client in self._client_list:
                client.socket.close()
            for thread in client_threads:
                thread.join()
            print("Server shut down due to error.")

#
if __name__ == "__main__":
    try:
        server = Server("0.0.0.0")
        server.start()
    except Exception as e:
        print(e)