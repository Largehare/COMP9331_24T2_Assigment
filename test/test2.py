import sys
from pathlib import Path
parent_dir = Path(__file__).resolve().parent.parent
sys.path.append(str(parent_dir))
import threading
import unittest
import client  # Ensure this module is correctly imported


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

    def test_case1(self):
        client_ = client.Client(54321, "example.com.", "A", 5)
        self.my_assert(client_, [("example.com.", "A", "93.184.216.34")], [], [])

    def test_case2(self):
        client_ = client.Client(54321, "example.com.", "A", -1)
        with self.assertRaises(TimeoutError):
            client_.send_request()

    def test_case3(self):
        client_ = client.Client(54321, "foo.bar.example.com.", "CNAME", 5)
        self.my_assert(
            client_,
            [("foo.bar.example.com.", "CNAME", "api.example.com.")],
            [],
            [],
        )

    def test_case4(self):
        client_ = client.Client(54321, ".", "NS", 5)
        self.my_assert(
            client_,
            [(".", "NS", "b.root-servers.net."), (".", "NS", "a.root-servers.net.")],
            [],
            [],
        )

    def test_case5(self):
        client_ = client.Client(54321, "docs.example.com.", "CNAME", 5)
        self.my_assert(
            client_,
            [("docs.example.com.", "CNAME", "www.example.com.")],
            [],
            [],
        )

    def test_case6(self):
        client_ = client.Client(54321, "cdn.example.com.", "CNAME", 5)
        self.my_assert(
            client_,
            [("cdn.example.com.", "CNAME", "api.example.com.")],
            [],
            [],
        )

    def test_case7(self):
        client_ = client.Client(54321, "archive.example.com.", "NS", 5)
        self.my_assert(
            client_,
            [("archive.example.com.", "NS", "ns3.archive.example.com.")],
            [],
            [],
        )

    def test_case8(self):
        client_ = client.Client(54321, "shop.example.com.", "A", 5)
        self.my_assert(
            client_,
            [("shop.example.com.", "A", "93.184.216.36")],
            [],
            [],
        )

    def test_case9(self):
        client_ = client.Client(54321, "example.net.", "NS", 5)
        self.my_assert(
            client_,
            [("example.net.", "NS", "service.example.net.")],
            [],
            [],
        )

    def test_case10(self):
        client_ = client.Client(54321, "forum.example.com.", "CNAME", 5)
        self.my_assert(
            client_,
            [("forum.example.com.", "CNAME", "www.example.com.")],
            [],
            [],
        )



if __name__ == "__main__":
    unittest.main()
