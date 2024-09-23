#! /usr/bin/env python3
import datetime
import socket
import sys
import threading
import time
import random
from message import *
import utils
import queue

def main():
    if len(sys.argv) != 2:
        sys.exit(f"Usage: {sys.argv[0]} <server_port>")

    try:
        server_port = int(sys.argv[1])
    except ValueError:
        sys.exit("Error: server_port must be an integer.")

    server = Server(server_port)
    try:
        server.run()
    except KeyboardInterrupt:
        if server.socket:
            server.close()
        print("Server stopped.")


class Server:

    def __init__(self, server_port: int = 54321, rr_path: str = "master.txt") -> None:
        """Initialise the server with the specified port and bank.
        Args:
            server_port (int): The UDP port to listen on.
        """
        self.server_port = server_port
        self.record_cache = utils.split_file(rr_path)
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    def run(self):
        """The main server loop, where the server listens for incoming requests."""
        print(f"Server running on port {self.server_port}...")
        print("Press Ctrl+C (Ctrl+Fn+B in powershell) to exit.")
        self.socket.bind(("127.0.0.1", self.server_port))
        while True:
            try:
                data, addr = self.socket.recvfrom(1024)
                #  multi-threaded version
                client_thread = threading.Thread(
                    target=self.process_request, args=(data, addr)
                )
                client_thread.start()
            except OSError as e:
                print(f"Error: {e}")
            except ValueError as e:
                print(f"Error: {e}")

    def find_answer(self, qname: str, qtype: str) -> list:
        # This method should continue to loop until an answer is found or no more CNAME redirections are possible.
        res = []
        visited = set()
        queue_ = queue.Queue()
        queue_.put(qname)
        # BFS
        while not queue_.empty():
            current_qname = queue_.get()
            if current_qname in visited:
                continue
            visited.add(current_qname)
            for record in self.record_cache:
                if record[0] == current_qname:
                    if record[1] == "CNAME" and qtype != "CNAME":
                        res.append(record)
                        queue_.put(record[2])  # Redirect to canonical name
                    elif record[1] == qtype:
                        res.append(record)
        return res

    # if qname and qtype are totally matched
    def find_authority(self, qname: str) -> list:
        def bfs():
            # BFS
            while not queue_.empty():
                current_qname = queue_.get()
                if current_qname in visited:
                    continue
                visited.add(current_qname)
                for record in self.record_cache:
                    if record[0] == current_qname:
                        res.append(record)
                        queue_.put(record[2])

        res = []
        queue_ = queue.Queue()
        visited = set()

        qname = qname.split(".", 1)[1]
        # if not found, find authority iterate until only "." is left
        while qname.find(".") != -1:
            queue_.put(qname)
            bfs()
            if "NS" in [record[1] for record in res]:
                return res
            qname = qname.split(".", 1)[1]

        # find root
        queue_.put(".")
        bfs()
        return res

    def process_request(self, data: bytes, addr: tuple[str, int]) -> None:
        # Delay processing the query for a random amount of time of 0, 1, 2, 3, or 4 seconds.
        time_delay = random.randint(0, 4)
        data = data.decode()
        message = ClientMessage.from_str(data)
        if message.question[0][-1] != ".":
            self.socket.sendto("qname must end with .".encode(), addr)
            raise ValueError("qname must end with .")
        qid = message.header["qid"]
        qname, qtype = message.question
        # <timestamp> <snd|rcv> <client_port>: <qid> <qname> <qtype> (delay: <delay>s)
        print(
            f"{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]} rcv {addr[1]}: {message.header['qid']} {qname} {qtype} (delay: {time_delay}s)"
        )
        time.sleep(time_delay)

        records = self.find_answer(qname, qtype)
        if not any(qtype == record[1] for record in records):
            records += self.find_authority(qname)
        response_cls = ServerMessage()
        response_cls.header["qid"] = qid
        response_cls.question = (qname, qtype)
        target = [qname]  # qname and its Canonical Name
        # classifying the records
        for record in records:
            if record[0] in target and record[1] == "CNAME":
                response_cls.answer.append(record)
                target.append(record[2])
            elif record[0] in target and record[1] == qtype:
                response_cls.answer.append(record)
            elif record[1] == "NS":
                response_cls.authority.append(record)
            else:
                response_cls.additional.append(record)
        response = response_cls.construct()
        self.socket.sendto(response.encode(), addr)
        print(f"{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]} snd {addr[1]}: {qid} {qname} {qtype}")

    def close(self):
        self.socket.close()


if __name__ == "__main__":
    main()
