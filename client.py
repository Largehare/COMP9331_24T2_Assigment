#! /usr/bin/env python3
import argparse
import random
import socket
from message import *

UINT16_MAX = 65535

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("server_port", type=int, help="UDP port of the server")
    parser.add_argument("qname", type=str, help="query name")
    parser.add_argument("qtype", type=str, help="query type")
    parser.add_argument("timeout", type=int, help="timeout")
    args = parser.parse_args()
    if args.qname[-1] != ".":
        raise ValueError("qname must end with .")
    client = Client(args.server_port, args.qname, args.qtype, args.timeout)

    client.send_request()


class Client:

    def __init__(self, port: int, qname: str, qtype: str, timeout: int) -> None:
        if timeout < 0:
            raise TimeoutError("timed out")
        self.dst_port = port
        self.dst = "127.0.0.1"
        self.qid = random.randint(0, UINT16_MAX)
        self.message = ClientMessage(self.qid, qname, qtype)
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.settimeout(timeout)
        self.timeout_flag = False

    def send_request(self) -> None:
        try:
            self.socket.sendto(
                self.message.construct().encode(), (self.dst, self.dst_port)
            )
            data, addr = self.socket.recvfrom(1024)
            data = data.decode()
            self.feedback = ServerMessage(data)
            output = ''
            output += f'ID: {self.feedback.header["qid"]}\n\n'
            output += f'QUESTION SECTION:\n'
            output += f'{self.feedback.question[0]:<20}\t{self.feedback.question[1]:<10}\n'
            if self.feedback.answer:
                output += '\n'
                output += f'ANSWER SECTION:\n'
                for record in self.feedback.answer:
                    output += f'{record[0]:<20}\t{record[1]:<10}\t{record[2]}\n'
            if self.feedback.authority:
                output += '\n'
                output += f'AUTHORITY SECTION:\n'
                for record in self.feedback.authority:
                    output += f'{record[0]:<20}\t{record[1]:<10}\t{record[2]}\n'
            if self.feedback.additional:
                output += '\n'
                output += f'ADDITIONAL SECTION:\n'
                for record in self.feedback.additional:
                    output += f'{record[0]:<20}\t{record[1]:<10}\t{record[2]}\n'
            output += '\n'
            print(output)
        except socket.timeout:
            # used for testing
            self.timeout_flag = True
            print("timed out")
    def __del__(self):
        self.socket.close()

if __name__ == "__main__":
    main()
