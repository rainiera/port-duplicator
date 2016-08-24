"""
Mirror newline-delimited UDP traffic on one port to N listener ports via TCP,
without multicasting or iptables.

This traffic duplicator requires that NUM_PORTS consecutive ports
from TCP_START_PORT are being listened on (see `-h`).

Thread-1 listens for UDP packets on UDP_PORT.
Thread-2 sends TCP packets that have been received on UDP_PORT
by the first thread to TCP_PORTS using a thread pool.
"""

import os
import sys
import socket
import argparse
import logging

parent_dir = os.path.abspath(os.path.dirname(__file__))
vendor_dir = os.path.join(parent_dir, "grove")
sys.path.append(vendor_dir)
from grove import grove

from Queue import Queue
from functools import partial
from threading import Thread
from multiprocessing.dummy import Pool as ThreadPool

DEBUG = True
BUFFER_SIZE = 1024

msg_queue = Queue()


class Producer(Thread):

    def __init__(self, config):
        super(Producer, self).__init__()
        self.config = config
        self.udp_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    def run(self):
        """Listen for packets from UDP_PORT via UDP and add them to the global queue
        """
        global msg_queue
        self.udp_sock.bind((self.config.host, self.config.udp_port))
        while True:
            try:
                data, addr = self.udp_sock.recvfrom(BUFFER_SIZE)
                msg_queue.put(data)
                if not data:
                    continue
                print "produced data %s (received from %s via UDP and enqueued):" % (data, self.config.udp_port)
            except socket.error as e:
                print "failed to produce:", e
                return -1


class Consumer(Thread):

    def __init__(self, config):
        super(Consumer, self).__init__()
        self.config = config
        self.socks = {port_num: None for port_num in config.tcp_ports}  # Port number to socket object table

    def run(self):
        """Dequeue messages and send them to TCP_PORT via TCP
        """
        global msg_queue
        for port_num in self.config.tcp_ports:
            """For each port number specified by the config,
            attempt to connect 5 times. If that isn't working, its corresponding
            socket in the socks table will be None.
            """
            for i in range(0, 5):
                sock = self._try_conn(port_num)
                if sock:
                    self.socks[port_num] = sock
                    break
                else:
                    self.socks[port_num] = None
        while True:
            try:
                if msg_queue.empty():
                    continue
                else:
                    data = msg_queue.get()
                    _send_partial = partial(self._send, data=data)
                    print self.socks
                    pool = ThreadPool(self.config.num_ports)
                    results = pool.map(_send_partial, self.config.tcp_ports)
                    pool.close()
                    pool.join()
                    print "Success conditions from thread pool: %s\n" % (results)
                    successes = filter(lambda x: self.socks[x] is not None, self.config.tcp_ports)
                    print "Ports still alive: %s\n" % (successes)
                    print "Consumed data (dequeued and sent to %s via TCP): %s" % (str(successes), data)
            except BaseException as e:
                print "failed to consume:", e
                return -1

    def _send(self, port_num, data):
        """Wrapper around socket.send() that tries harder and handles errors more gracefully.
        Returns True/False upon success/failure.
        """
        try:
            self.socks[port_num].send(data)
            return True
        except BaseException:
            for i in range(0, 5):
                sock = self._try_conn(port_num)
                if sock:
                    self.socks[port_num] = sock
                    self._send(port_num, data)
                    return True
                else:
                    self.socks[port_num] = None
            return False
        finally:
            pass

    def _try_conn(self, port_num):
        """Attempts to connect a socket given a port number.
        Sets the port number key in the socket table and returns the socket object if available.
        """
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.connect((self.config.host, port_num))
            self.socks[port_num] = sock
            return sock
        except BaseException as e:
            print "Connection on %s failed because of %s\n" % (port_num, e)
            self.socks[port_num] = None
            return None

    def __str__(self):
        return str((self.config.__str__, self.socks))

    def __repr__(self):
        return self.__str__()


class TrafficConfig:
    config = None
    host = "localhost"
    udp_port = 8081
    tcp_start_port = 8082
    num_ports = 2
    tcp_ports = None

    log_directory = None
    log_level = logging.INFO
    logger = None

    def load(self):
        """Load TrafficConfig from config json file if available, and calculate tcp_ports.
        """
        grove.set_config(self, self.config)
        self.tcp_ports = [self.tcp_start_port + i for i in range(0, self.num_ports)]
        self.logger = grove.get_logger(self, DEBUG)

    def __str__(self):
        return str({"config": self.config,
                    "host": self.host,
                    "udp_port": self.udp_port,
                    "tcp_start_port": self.tcp_start_port,
                    "num_ports": self.num_ports,
                    "tcp_ports": self.tcp_ports})

    def __repr__(self):
        return self.__str__()


if __name__ == "__main__":
    _config = TrafficConfig()
    parser = argparse.ArgumentParser(description="Mirror newline-delimited UDP traffic on one port to N listener ports via TCP without multicasting or iptables.")
    parser.add_argument("--config", metavar="config", type=str, help="path to a config file")
    parser.add_argument("--host", metavar="host", type=str, help="specify hostname")
    parser.add_argument("--udp_port", metavar="udp_port", type=int, help="port to mirror from")
    parser.add_argument("--tcp_start_port", metavar="tcp_start_port", type=int, help="first port to mirror to")
    parser.add_argument("--num_ports", metavar="num_ports", type=int, help="specify number of ports to mirror to")
    args = parser.parse_args()
    parser.parse_args(namespace=_config)
    _config.load()
    # Just to confirm that the configurations are correct
    # print _config
    try:
        Producer(_config).start()
        Consumer(_config).start()
    except Exception as e:
        print "Failed to start thread because %s" % (e)
        sys.exit(-1)
