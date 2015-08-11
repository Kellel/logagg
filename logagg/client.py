import os
import argparse
import fileinput
import zmq
import sys
import logging

from message import ZMQPushSocket, FileInput

log = logging.getLogger(__name__)

def client(infile, name="cli-client"):

    with ZMQPushSocket("tcp://127.0.0.1:7770") as sock:

        #sock.set_hwm(50)

        log.info("STARTUP")

        log.debug(infile)

        with FileInput(infile) as f:
            for line in f:
                log.debug(line)
                message = {"app": name, "msg": line}
                log.debug(message)
                sock.send_json(message)
                log.debug("SENT")

        log.info("SHUTDOWN")
        infile.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--name")
    parser.add_argument('-f', '--follow')
    parser.add_argument('infile', nargs='?', type=argparse.FileType('r'), default=sys.stdin)
    args = parser.parse_args()
    logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)

    try:
        if args.name:
            client(infile=args.infile, name=args.name)
        else:
            client(infile=args.infile)
    except KeyboardInterrupt:
        pass

