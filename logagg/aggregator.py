#
# Log Aggregator
#
# TODO: If this ends up being too slow performance might be increased by using gevent workers
#
#                    [  RECIEVER  ]              # The master listens on the PULL socket (`reveiver`)
#                                                # and puts each item in a seperate queue based on the app name
#                     /           \
#          [ gevent.Queue ] [ gevent.Queue ]     # We can get the fullness of each queue to monitor the performance of each worker
#                   |               |
#       [ gevent.Greenlet ] [ gevent.Greenlet ]  # Each thread will deal with its own
#       [   "portal-live" ] [   "portal-dev"  ]  # file this way you wont have to deal with locking the open file
#                     \           /
#                   [ gevent.Queue ]             # As with the worker queue we can monitor the fullness of the output queue
#                          |
#                      [ PUSHER ]                # Relay messages to logstash using the PUSH socket ('sender')
#
import sys
import os
import datetime
import logging

import zmq
import collections

from message import ZMQPushSocket,ZMQPullSocket

LOG_FILE_PATH = os.path.join(os.path.dirname(__file__), "tmp")
DAEMON_LOG_FILE = os.path.join(LOG_FILE_PATH, "logger-daemon.log")
logging.basicConfig(filename=DAEMON_LOG_FILE, level=logging.DEBUG)
log = logging.getLogger('logger')

HWM = 1000

class LogAggregator(object):
    def __init__(self):
        log.debug("Checking for LOG_FILE_PATH at %s", LOG_FILE_PATH)
        if not os.path.exists(LOG_FILE_PATH):
            log.debug("Creating LOG_FILE_PATH at %s", LOG_FILE_PATH)
            os.makedirs(LOG_FILE_PATH)
        self.files = {}
        self.start_time = datetime.datetime.now()
        self.stats = collections.Counter()

    def run(self):
        context = zmq.Context()

        # Bind sockets
        # Using a context manager ensures that we will always close the sockets
        # I think it's also more '`pythonic`' or whatever
        with ZMQPullSocket("tcp://0.0.0.0:7770", context, bind=True) as receiver:
            with ZMQPushSocket("tcp://127.0.0.1:7777", context) as sender:

                receiver.set_hwm(HWM)
                sender.set_hwm(HWM)

                # Get a json object from the backend instances
                for item in receiver:
                    self.work(item, sender)


    def work(self, message, sender):
        log.debug("WORK: %s", str(message))

        application = message['app']
        if application == None:
            application = "UNKNOWN-SENDER"

        msg = message['msg'].strip()
        log.info("JOB [FOR: {}] {}".format(application, msg))

        if not application in self.files or self.files[application].closed:
            log.info("OPENING: %s", application)
            self.files[application] = open(os.path.join(LOG_FILE_PATH, application), 'a')

        log.debug("Writing line to file")
        self.files[application].write(msg + "\n")
        self.files[application].flush()

        log.debug("Relaying MSG")
        sender.send_json({"app-name": application, "msg": msg})
        log.debug("JOB Complete.")
        self.stats["total"] += 1
        self.stats[application] += 1

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.cleanup()
        self.print_stats()

    def cleanup(self):
        log.debug("Closing %d log files", len(self.files))
        for item in self.files.values():
            item.close()

    def print_stats(self):
        stop_time = datetime.datetime.now()
        log.info("======= SHUTTING DOWN =======")
        log.info("Running time: %s", stop_time - self.start_time)
        total = self.stats["total"]
        del self.stats["total"]
        log.info("TOTAL REQUESTS: %s", total)
        for key, value in self.stats.items():
            log.info("REQUESTS FOR [%s]: %s", key, value)


if __name__ == "__main__":
    with LogAggregator() as logger:
        try:
            logger.run()
        except KeyboardInterrupt:
            pass

    logging.shutdown()
