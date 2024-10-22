import socket
import threading
import time


class Client:

    #init new client
    def __init__(self, HOST="127.0.0.1"):
        #self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.HOST = HOST
        self.name = ""
        self.id = 0
        self._isListening = True

    #this function returns first listening port, if returns -1 then there is none
    def __getListetnigPort(self, address):
        #print("__getListetnigPort")
        test_socket = None
        for port in range(40000, 60001):
            try:
                test_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                test_socket.connect((address, port))
                self.socket = test_socket
                return port
            except OSError:
                test_socket.close()
                continue
        return -1

    #function in a thread that listens a new message from the server
    def __listen(self):
        self.socket.setblocking(False)
        while self._isListening:
            #print("Listening...")
            try:
                data = self.socket.recv(1024)
                if not data:
                    continue
                # elif data == "Who are you":
                #     continue
                print(data.decode("utf-8"))
            except BlockingIOError:
                time.sleep(0.1)
                continue
            except OSError:
                pass

    def start(self):
        lst_port = self.__getListetnigPort(self.HOST)

        #if -1 then there is not listetning port
        if lst_port == -1:
            raise RuntimeError("There is no listening port!")

        #section where users enters it's name
        try:
            line = str()
            nameNotEtered = True
            data = self.socket.recv(1024)
            data = data.decode("utf-8")
            while nameNotEtered:
                print(data)
                line = input("#> ")
                if len(line) != 0:
                    nameNotEtered = False
        except BrokenPipeError:
            print("Server is down.")
            self.socket.close()
            return
        except KeyboardInterrupt:
            print("Connection interrupted!")
            self.socket.close()
            return

        self.socket.send(line.encode())

        #thread is listening a new message from a server
        thread = threading.Thread(target=self.__listen)
        thread.start()

        isRunning = True

        while isRunning:
            try:
                line = input("> ")
                if len(line) == 0:
                    continue
                elif line == "QUIT":
                    raise KeyboardInterrupt
                self.socket.sendall(line.encode())
            except KeyboardInterrupt:
                self._isListening = False
                isRunning = False
                self.socket.send(b"QUIT")
                self.socket.close()
                thread.join()
            except BrokenPipeError:
                print(f"Connection with server is broken. {chr(10)}Shutting down...")
                self._isListening = False
                isRunning = False
                self.socket.close()
                thread.join()


if __name__ == "__main__":
    try:
        client = Client("127.0.0.1")
        client.start()
    except Exception as e:
        print(e)