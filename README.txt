Log Aggregator
--------------


  [ uwsgi zmq-logger ] [ uwsgi zmq-logger ] [ uwsgi zmq-logger ]
                    \           |            /
                     \__________|___________/
                                |                     ---- file1.txt
                   _____________|_____________       /
                  [_______log aggregator______] ---- ----- file2.txt
                                |                    \
                      [ zmq logstash input ]          \___ file3.txt
