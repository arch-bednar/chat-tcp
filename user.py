class user:

    def __init__(self, _socket, _name):
        self._socket = _socket
        self._name = _name

    @property
    def name(self):
        return self._name

    @property
    def id(self):
        return self._socket.fileno()

    @property
    def socket(self):
        return self._socket

    def __str__(self):
        return self._name+"<"+str(self._socket.fileno())+">"


