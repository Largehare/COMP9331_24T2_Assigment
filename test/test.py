import sys
from pathlib import Path

parent_dir = Path(__file__).resolve().parent.parent
sys.path.append(str(parent_dir))
import unittest
import message
import server
import client
import utils
import threading

server_port = 54333
class TestClient(unittest.TestCase):
    def setUp(self) -> None:

        return super().setUp()

    def my_assert(
        self,
        client_: client.Client,
        answer_expected: list,
        authority_expected: list,
        additional_expected: list,
    ):
        client_.send_request()
        self.assertEqual(client_.message.header["qid"], client_.feedback.header["qid"])
        self.assertEqual(client_.message.question, client_.feedback.question)

        self.assertEqual(client_.feedback.answer, answer_expected)
        self.assertEqual(client_.feedback.authority, authority_expected)
        self.assertEqual(client_.feedback.additional, additional_expected)

    def case1(self):
        client_ = client.Client(server_port, "example.com.", "A", 5)
        self.my_assert(client_, [("example.com.", "A", "93.184.215.14")], [], [])

    def case2(self):
        client_ = client.Client(server_port, "example.com.", "A", 0.01)
        client_.send_request()
        self.assertEqual(client_.timeout_flag, True)
            
        

    def case3(self):
        client_ = client.Client(server_port, "bar.example.com.", "CNAME", 5)
        self.my_assert(
            client_,
            [("bar.example.com.", "CNAME", "foobar.example.com.")],
            [],
            [],
        )

    def case4(self):
        client_ = client.Client(server_port, ".", "NS", 5)
        self.my_assert(
            client_,
            [(".", "NS", "b.root-servers.net."), (".", "NS", "a.root-servers.net.")],
            [],
            [],
        )

        # additional_expected or [] ?

    def case5(self):
        client_ = client.Client(server_port, "bar.example.com.", "A", 5)
        self.my_assert(
            client_,
            [
                ("bar.example.com.", "CNAME", "foobar.example.com."),
                ("foobar.example.com.", "A", "192.0.2.23"),
                ("foobar.example.com.", "A", "192.0.2.24"),
            ],
            [],
            [],
        )

    def case6(self):
        client_ = client.Client(server_port, "foo.example.com.", "A", 5)
        self.my_assert(
            client_,
            [
                ("foo.example.com.", "CNAME", "bar.example.com."),
                ("bar.example.com.", "CNAME", "foobar.example.com."),
                ("foobar.example.com.", "A", "192.0.2.23"),
                ("foobar.example.com.", "A", "192.0.2.24"),
            ],
            [],
            [],
        )

    def case7(self):
        client_ = client.Client(server_port, "example.org.", "A", 5)
        self.my_assert(
            client_,
            [],
            [(".", "NS", "b.root-servers.net."), (".", "NS", "a.root-servers.net.")],
            [("a.root-servers.net.", "A", "198.41.0.4")],
        )

    def case8(self):
        client_ = client.Client(server_port, "example.org.", "CNAME", 5)
        self.my_assert(
            client_,
            [],
            [(".", "NS", "b.root-servers.net."), (".", "NS", "a.root-servers.net.")],
            [("a.root-servers.net.", "A", "198.41.0.4")],
        )

    def case9(self):
        client_ = client.Client(server_port, "example.org.", "NS", 5)
        self.my_assert(
            client_,
            [],
            [(".", "NS", "b.root-servers.net."), (".", "NS", "a.root-servers.net.")],
            [("a.root-servers.net.", "A", "198.41.0.4")],
        )

    def case10(self):
        client_ = client.Client(server_port, "www.metalhead.com.", "A", 5)
        self.my_assert(
            client_,
            [("www.metalhead.com.", "CNAME", "metalhead.com.")],
            [("com.", "NS", "d.gtld-servers.net.")],
            [("d.gtld-servers.net.", "A", "192.31.80.30")],
        )

    def test_multithread(self):
        threads = []
        func_names = ["case" + str(i + 1) for i in range(10)]
        for func_name in func_names:
            func = getattr(self, func_name)
            thread = threading.Thread(target=func)
            threads.append(thread)
        for thread in threads:
            thread.start()
            # thread.join()  # if join here, it will be a single thread
        for thread in threads:
            thread.join()


class TestSplit(unittest.TestCase):
    def test_split(self):
        path = "master.txt"
        cache = utils.split_file(path)
        self.assertEqual(cache[0], ("foo.example.com.", "CNAME", "bar.example.com."))


class TestMessageDeconstruct(unittest.TestCase):
    def test_deconstruct(self):
        data = "ID: 100\r\nQUESTION SECTION:\nexample.com.\tA\r\nANSWER SECTION:\nexample.com.\tA\t93.184.216.34\r\nAUTHORITY SECTION:\nexample.com.\tNS\tdns1.icann.org.\r\nADDITIONAL SECTION:\ndns1.icann.org.\tA\t192.0.32.7"
        msg = message.ServerMessage(data)
        self.assertEqual(msg.header["qid"], 100)
        self.assertEqual(msg.question, ("example.com.", "A"))
        self.assertEqual(msg.answer, [("example.com.", "A", "93.184.216.34")])
        self.assertEqual(msg.authority, [("example.com.", "NS", "dns1.icann.org.")])
        self.assertEqual(msg.additional, [("dns1.icann.org.", "A", "192.0.32.7")])


class TestMessageConstruct(unittest.TestCase):
    def test_client_construct(self):
        msg = message.ClientMessage(100, "example.com.", "A")
        out = msg.construct()
        expected = "ID: 100\r\nQUESTION SECTION:\nexample.com.\tA"
        self.assertEqual(out, expected)

    def test_server_construct(self):
        msg = message.ServerMessage(
            "ID: 100\r\nQUESTION SECTION:\nexample.com.\tA\r\nANSWER SECTION:\nexample.com.\tA\t93.184.216.34\r\nAUTHORITY SECTION:\nexample.com.\tNS\tdns1.icann.org.\r\nADDITIONAL SECTION:\ndns1.icann.org.\tA\t192.0.32.7"
        )
        out = msg.construct()
        expected = "ID: 100\r\nQUESTION SECTION:\nexample.com.\tA\r\nANSWER SECTION:\nexample.com.\tA\t93.184.216.34\r\nAUTHORITY SECTION:\nexample.com.\tNS\tdns1.icann.org.\r\nADDITIONAL SECTION:\ndns1.icann.org.\tA\t192.0.32.7"
        self.assertEqual(out, expected)


class TestServer(unittest.TestCase):
    pass


class TestServerFindAnswer(unittest.TestCase):
    def test_single_result(self):
        server_ = server.Server(server_port)
        res = server_.find_answer("example.com.", "A")
        self.assertEqual(res, [("example.com.", "A", "93.184.215.14")])

    def test_multiple_result(self):
        server_ = server.Server(server_port)
        res = server_.find_answer(".", "NS")
        self.assertEqual(
            res,
            [
                (".", "NS", "b.root-servers.net."),
                (".", "NS", "a.root-servers.net."),
            ],
        )


class TestClientConstructor(unittest.TestCase):
    def test_construct(self):
        msg = message.ClientMessage(100, "example.com.", "A")
        self.assertEqual(msg.header["qid"], 100)
        self.assertEqual(msg.question, ("example.com.", "A"))

    def test_construct_str(self):
        msg = message.ClientMessage.from_str(
            "ID: 100\r\nQUESTION SECTION:\nexample.com.\tA"
        )
        self.assertEqual(msg.header["qid"], 100)
        self.assertEqual(msg.question, ("example.com.", "A"))


if __name__ == "__main__":
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    suite.addTests(
        [
            loader.loadTestsFromTestCase(TestSplit),
            loader.loadTestsFromTestCase(TestMessageConstruct),
            loader.loadTestsFromTestCase(TestMessageDeconstruct),
            loader.loadTestsFromTestCase(TestServerFindAnswer),
            loader.loadTestsFromTestCase(TestClientConstructor),
            # loader.loadTestsFromTestCase(TestServer),
            loader.loadTestsFromTestCase(TestClient),
            # loader.loadTestsFromName('case7', TestClient),
        ]
    )
    # unittest.main()
    # Run the test suite
    runner = unittest.TextTestRunner()
    runner.run(suite)
