class Message:
    def __init__(self, qid: int, qtype: str, qname: str) -> None:
        # qid 16-bit unsigned integer
        self.header = dict([("qid", qid)])
        # the server question section duplicates the question section of the query.
        self.question = (qname, qtype)

    def construct(self) -> None:
        # TODO  Construct the DNS message from the header, question, answer,
        pass

    def deconstruct(self, data: str) -> None:
        pass


class ClientMessage(Message):

    def __init__(self, qid: int, qname: str, qtype: str) -> None:
        super().__init__(qid, qtype, qname)

    @classmethod
    def from_str(cls, data: str) -> "ClientMessage":
        cls.deconstruct(cls, data)
        return cls

    def construct(self) -> str:
        message = ""
        message += f'ID: {self.header["qid"]}\r\n'
        message += f"QUESTION SECTION:\n{self.question[0]}\t{self.question[1]}"
        return message

    def deconstruct(self, data: str) -> None:
        lines = data.split("\r\n")
        self.header = {}
        self.question = ()
        for line in lines:
            if line == "":
                continue
            if "ID" in line:
                self.header["qid"] = int(line.split(": ")[1])
            elif "QUESTION SECTION" in line:
                self.question = tuple(line.split("\n")[1].split("\t"))


class ServerMessage(Message):
    def __init__(self, *args) -> None:
        self.header = {}
        self.question = ()
        self.answer = []
        self.authority = []
        self.additional = []
        if args and isinstance(args[0], str):
            data = args[0]
            self.deconstruct(data)
        

    def deconstruct(self, data: str) -> None:
        lines = data.split("\r\n")
        for line in lines:
            if line == "":
                continue
            if "ID" in line:
                self.header["qid"] = int(line.split(": ")[1])
            elif "QUESTION SECTION" in line:
                self.question = tuple(line.split("\n")[1].split("\t"))
            elif "ANSWER SECTION" in line:
                self.answer = [
                    tuple(answer.split("\t")) for answer in line.split("\n")[1:]
                ]
            elif "AUTHORITY SECTION" in line:
                self.authority = [
                    tuple(authority.split("\t")) for authority in line.split("\n")[1:]
                ]
            elif "ADDITIONAL SECTION" in line:
                self.additional = [
                    tuple(additional.split("\t")) for additional in line.split("\n")[1:]
                ]

    def construct(self) -> str:
        message = ""
        message += f'ID: {self.header["qid"]}\r\n'
        message += f"QUESTION SECTION:\n{self.question[0]}\t{self.question[1]}"
        if self.answer:
            message += "\r\n"
            message += "ANSWER SECTION:\n"
            for answer in self.answer:
                message += f"{answer[0]}\t{answer[1]}\t{answer[2]}\n"
            message = message.strip()
        if self.authority:
            message += "\r\n"
            message += "AUTHORITY SECTION:\n"
            for authority in self.authority:
                message += f"{authority[0]}\t{authority[1]}\t{authority[2]}\n"
            message = message.strip()
        if self.additional:
            message += "\r\n"
            message += "ADDITIONAL SECTION:\n"
            for additional in self.additional:
                message += f"{additional[0]}\t{additional[1]}\t{additional[2]}\n"
        return message.strip()
