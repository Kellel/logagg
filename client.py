import fileinput
import zmq
import sys
import logging

log = logging.getLogger(__name__)
logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)

ctx = zmq.Context()
sock = ctx.socket(zmq.PUSH)
sock.connect("tcp://127.0.0.1:7770")
sock.set_hwm(50)

log.info("STARTUP")

for line in fileinput.input():
    message = {"app": "cli-client", "msg": line}
    log.debug(message)
    sock.send_json(message)
    log.debug("SENT")

# FORCE TO EXIT IF THE CONNECTION IS FAIL
ctx.destroy(linger=1000)
log.info("SHUTDOWN")
