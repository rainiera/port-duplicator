/*
Program that sends UDP packets to CONN_PORT
*/

package main

import (
	"bufio"
	"fmt"
	"log"
	"net"
	"os"
)

const (
	CONN_HOST = ""
	CONN_PORT = 8081
	CONN_TYPE = "udp"
)

func main() {
	CONN_ADDR := net.UDPAddr{
		Port: CONN_PORT,
		IP:   net.ParseIP(CONN_HOST),
	}
	conn, err := net.DialUDP(CONN_TYPE, nil, &CONN_ADDR)
	if err != nil {
		log.Fatal(err)
	}
	defer conn.Close()
	fmt.Println("Client connection initiated")
	for {
		reader := bufio.NewReader(os.Stdin)
		fmt.Print("Text to send: ")
		text, _ := reader.ReadString('\n')
		fmt.Fprintf(conn, text+"\n")
	}
}
