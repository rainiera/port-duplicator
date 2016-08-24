# port-duplicator

Mirror newline-delimited UDP traffic on one port to N listener ports via TCP,
without multicasting or iptables.

For educational purposes as it also includes a custom logging and config-loading
infrastructure, `grove`.

## (Optional - for testing) Build static binaries for UDP client and TCP server

```
$ go build tcp_server.go
$ go build udp_client.go
```

## Example usage

Set up UDP input source (e.g., `\n`-delimited stdin):

```
$ ./udp_client 8081
Client connection initiated
Text to send: 
```

Set up TCP servers before allowing `mirror.py` to attempt to bind:

```
$ ./tcp_server 8082
Listening on port 8082...
```

```
$ ./tcp_server 8083
Listening on port 8083...
```

```
$ ./tcp_server 8084
Listening on port 8084...
```

Start traffic mirror:

```
$ python mirror.py -h
usage: mirror.py [-h] [--config config] [--host host] [--udp_port udp_port]
                 [--tcp_start_port tcp_start_port] [--num_ports num_ports]

Mirror newline-delimited UDP traffic on one port to N listener ports via TCP
without multicasting or iptables.

optional arguments:
  -h, --help            show this help message and exit
  --config config       path to a config file
  --host host           specify hostname
  --udp_port udp_port   port to mirror from
  --tcp_start_port tcp_start_port
                        first port to mirror to
  --num_ports num_ports
                        specify number of ports to mirror to

$ python mirror.py --udp_port 8081 --tcp_start_port 8082 --num_ports 3
```

## TODO

- unit tests
- Monit or daemontools supervise on server binaries, or `SO_REUSEADDR` socket option, since we can't reuse socket after close
