import zmq
import sys

ctx = zmq.Context()
sock = ctx.socket(zmq.PUSH)
sock.connect("tcp://127.0.0.1:7770")

for line in sys.stdin:
    message = {"app": "cli-client", "msg": line}
    sock.send_json(message)
