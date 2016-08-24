/*
Program that listens for TCP packets on argv[1:] (port1 . . . portN)
*/

package main

import (
	"bufio"
	"flag"
	"fmt"
	"io"
	"log"
	"net"
	"strconv"
	"strings"
)

func main() {
	ports := argparse()
	run(ports)
}

func argparse() []int {
	var ports []int
	var (
		start_port = flag.Int("p", -1, "provide a starting port")
		num_ports  = flag.Int("n", 0, "provide a number of ports")
	)
	flag.Parse()
	argv := flag.Args()
	if *start_port > -1 {
		if *num_ports <= 0 {
			log.Fatal("Must provide a number of ports if providing a starting port")
		} else {
			for i := 0; i < *num_ports; i++ {
				ports = append(ports, *start_port+i)
			}
		}
	} else {
		if len(argv) < 1 {
			log.Fatal("Must provide at least one port to listen on")
		}
		for _, arg := range argv {
			port, err := strconv.Atoi(arg)
			if err != nil {
				log.Fatal("All args must be valid port numbers (integers) if not using '-p' flag")
			}
			ports = append(ports, port)
		}
	}
	return ports
}

func run(ports []int) {
	// Can be adapted to listen to more ports simultaneously with more goroutines
	fmt.Println("Listening on port:", ports[0])

	ip := net.ParseIP("127.0.0.1")
	laddr := net.TCPAddr{IP: ip, Port: ports[0]}
	ln, err := net.ListenTCP("tcp", &laddr)
	if err != nil {
		log.Fatal(err)
	}

	conn, err := ln.AcceptTCP()
	conn.SetKeepAlive(true)
	if err != nil {
		log.Fatal(err)
	}

	defer conn.Close()
	for {
		message, err := bufio.NewReader(conn).ReadString('\n')
		if err != nil {
			if err == io.EOF {
				conn.Close()
			} else {
				log.Fatal(err)
			}
		}
		fmt.Print("Message received:", string(message))
		conn.Write([]byte("Ack\n"))
		newmessage := strings.TrimSpace(strings.ToUpper(message))
		fmt.Println(newmessage + " (echo)\n")
	}
}
