import argparse
import fileinput
import zmq
import sys
import logging

from message import ZMQPushSocket

log = logging.getLogger(__name__)

def client(infile, name="cli-client"):

    with ZMQPushSocket("tcp://127.0.0.1:7770") as sock:

        sock.set_hwm(50)

        log.info("STARTUP")

        for line in infile:
            message = {"app": name, "msg": line}
            log.debug(message)
            sock.send_json(message)
            log.debug("SENT")

        log.info("SHUTDOWN")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--name")
    parser.add_argument('infile', type=argparse.FileType('r'), default=sys.stdin)
    args = parser.parse_args()

    if args.name:
        client(infile=args.infile, name=args.name)
    else:
        client(infile=args.infile)

    logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)
