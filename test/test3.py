import sys
from pathlib import Path

parent_dir = Path(__file__).resolve().parent.parent
sys.path.append(str(parent_dir))
import unittest
import client


class TestDNSResolver(unittest.TestCase):
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

    def test_basic_a_records(self):
        client_ = client.Client(54321, "subdomain.example.com.", "A", 5)
        self.my_assert(
            client_, [("subdomain.example.com.", "A", "93.184.216.34")], [], []
        )

    def test_cname_records(self):
        client_ = client.Client(54321, "www.example.com.", "CNAME", 5)
        self.my_assert(client_, [("www.example.com.", "CNAME", "example.com.")], [], [])

    def test_ns_records(self):
        client_ = client.Client(54321, "example.com.", "NS", 5)
        self.my_assert(client_, [("example.com.", "NS", "ns.example.com.")], [], [])

    def test_multiple_a_records(self):
        client_ = client.Client(54321, "multi-a.example.com.", "A", 5)
        self.my_assert(
            client_,
            [
                ("multi-a.example.com.", "A", "192.168.0.1"),
                ("multi-a.example.com.", "A", "192.168.0.2"),
            ],
            [],
            [],
        )

    def test_cname_chain(self):
        client_ = client.Client(54321, "long-chain-cname.example.com.", "CNAME", 5)
        self.my_assert(
            client_,
            [
                (
                    "long-chain-cname.example.com.",
                    "CNAME",
                    "long-chain-cname-1.example.com.",
                ),
            ],
            [],
            [],
        )

    def test_cname_chain2(self):
        client_ = client.Client(54321, "long-chain-cname.example.com.", "A", 5)
        self.my_assert(
            client_,
            [
                (
                    "long-chain-cname.example.com.",
                    "CNAME",
                    "long-chain-cname-1.example.com.",
                ),
                (
                    "long-chain-cname-1.example.com.",
                    "CNAME",
                    "long-chain-cname-2.example.com.",
                ),
                (
                    "long-chain-cname-2.example.com.",
                    "CNAME",
                    "long-chain-cname-3.example.com.",
                ),
                (
                    "long-chain-cname-3.example.com.",
                    "CNAME",
                    "long-label-63characterslonglabel-123456789012345678901234567890123.a.",
                ),
            ],
            [('example.com.', 'NS', 'ns.example.com.')],
            [('ns.example.com.', 'A', '93.184.216.34')],
        )

    def test_ipv6_record(self):
        client_ = client.Client(54321, "ipv6.example.com.", "AAAA", 5)
        self.my_assert(
            client_,
            [("ipv6.example.com.", "AAAA", "2001:0db8:85a3:0000:0000:8a2e:0370:7334")],
            [],
            [],
        )

    def test_mx_record(self):
        client_ = client.Client(54321, "mail.example.com.", "MX", 5)
        self.my_assert(
            client_, [("mail.example.com.", "MX", "mailhost.example.com.")], [], []
        )

    # def test_wildcard_record(self):
    #     client_ = client.Client(54321, "anything.example.com.", "A", 5)
    #     self.my_assert(
    #         client_,
    #         [("anything.example.com.", "A", "192.0.2.1")],
    #         [],
    #         []
    #     )


if __name__ == "__main__":
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    suite.addTests(
        [
            loader.loadTestsFromTestCase(TestDNSResolver),
            # loader.loadTestsFromName("test_cname_chain2", TestDNSResolver),
        ]
    )
    # unittest.main()
    # Run the test suite
    runner = unittest.TextTestRunner()
    runner.run(suite)
