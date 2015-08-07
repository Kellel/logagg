import sys
import os

import logging
import zmq
from zmq.devices.basedevice import ProcessDevice

logging.basicConfig(stream=sys.stderr, level=logging.INFO)
log = logging.getLogger('logger')

LOG_FILE_PATH = "./log"
HWM = 50

class LogWorker(object):
    def __init__(self):
        log.debug("Checking for LOG_FILE_PATH at %s", LOG_FILE_PATH)
        if not os.path.exists(LOG_FILE_PATH):
            log.debug("Creating LOG_FILE_PATH at %s", LOG_FILE_PATH)
            os.makedirs(LOG_FILE_PATH)
        self.files = {}

    def run(self):
        context = zmq.Context()

        receiver = context.socket(zmq.PULL)
        receiver.set_hwm(HWM)
        receiver.bind("tcp://127.0.0.1:7770")

        sender = context.socket(zmq.PUSH)
        sender.set_hwm(HWM)
        sender.connect("tcp://127.0.0.1:7777")

        while True:
            work = receiver.recv_json()
            log.debug("WORK: %s", str(work))

            application = work['app']
            msg = work['msg'].strip()
            log.info("JOB [FOR: {}] {}".format(application, msg))

            if not application in self.files or self.files[application].closed:
                log.info("OPENING: %s", application)
                self.files[application] = open(os.path.join(LOG_FILE_PATH, application), 'a')

            log.debug("Writing line to file")
            self.files[application].write(msg + "\n")
            self.files[application].flush()

            log.debug("Relaying MSG")
            sender.send_json(work)
            log.debug("JOB Complete.")

    def cleanup(self):
        log.debug("Closing %d log files", len(self.files))
        for item in self.files.values():
            item.close()

if __name__ == "__main__":
    logger = LogWorker()
    try:
        logger.run()
    except KeyboardInterrupt:
        pass
    finally:
        logger.cleanup()
