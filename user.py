import socket

class user:
#
    def __init__(self, _socket, _name="", _id=""):
        self._socket = _socket
        self._name = _name
        self._id = _id

    @property
    def name(self):
        return self._name

    @property
    def id(self):
        return self._id

    @property
    def socket(self):
        return self._socket

    def __str__(self):
        return self._name+"<"+self._id+">"

    def setName(self, name):
        self._name = name

    def setId(self, id):
        self._id = id

    def setData(self, data):
        self.setId(data[data.find("<")+1:data.find(">")])
        self.setName(data[:data.find("<")])