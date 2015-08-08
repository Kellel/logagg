import zmq

class ZMQSocket(object):
    def __init__(self, address, type, context=None, bind=False):
        self.address = address
        self.type = type
        self.bind = bind
        self.context = context or zmq.Context()
        self.socket = self.context.socket(self.type)


    def __enter__(self):
        if self.bind:
            self.socket.bind(self.address)
        else:
            self.socket.connect(self.address)
        return ZMQSocketReader(self.socket)

    def __exit__(self, exc_type, exc_value, traceback):
        self.socket.close(linger=1000)


class ZMQPushSocket(ZMQSocket):
    def __init__(self, address, context=None, bind=False):
        super(ZMQPushSocket, self).__init__(address, zmq.PUSH, context, bind)

class ZMQPullSocket(ZMQSocket):
    def __init__(self, address, context=None, bind=False):
        super(ZMQPullSocket, self).__init__(address, zmq.PULL, context, bind)

class ZMQSocketReader(object):
    def __init__(self, socket):
        self.socket = socket
        self.send_json = self.socket.send_json

    def __iter__(self):
        return self

    def next(self):
        work = self.socket.recv_json()
        return work

    def set_hwm(self, hwm):
        self.socket.set_hwm(hwm)
