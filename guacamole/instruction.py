ERROR_MAP = {
    "256": ("UNSUPPORTED", "The requested operation is unsupported."),
    "512": (
        "SERVER_ERROR",
        "An internal error occurred, and the operation could not be performed.",
    ),
    "513": (
        "SERVER_BUSY",
        "The operation could not be performed because the server is busy.",
    ),
    "514": (
        "UPSTREAM_TIMEOUT",
        "The upstream server is not responding. In most cases, the upstream server is the remote desktop server.",
    ),
    "515": (
        "UPSTREAM_ERROR",
        "The upstream server encountered an error. In most cases, the upstream server is the remote desktop server.",
    ),
    "516": (
        "RESOURCE_NOT_FOUND",
        "An associated resource, such as a file or stream, could not be found, and thus the operation failed.",
    ),
    "517": (
        "RESOURCE_CONFLICT",
        "A resource is already in use or locked, preventing the requested operation.",
    ),
    "518": (
        "RESOURCE_CLOSED",
        "The requested operation cannot continue because the associated resource has been closed.",
    ),
    "519": (
        "UPSTREAM_NOT_FOUND",
        "The upstream server does not appear to exist, or cannot be reached over the network. In most cases, the upstream server is the remote desktop server.",
    ),
    "520": (
        "UPSTREAM_UNAVAILABLE",
        "The upstream server is refusing to service connections. In most cases, the upstream server is the remote desktop server.",
    ),
    "521": (
        "SESSION_CONFLICT",
        "The session within the upstream server has ended because it conflicts with another session. In most cases, the upstream server is the remote desktop server.",
    ),
    "522": (
        "SESSION_TIMEOUT",
        "The session within the upstream server has ended because it appeared to be inactive. In most cases, the upstream server is the remote desktop serve",
    ),
    "523": (
        "SESSION_CLOSED",
        "The session within the upstream server has been forcibly closed. In most cases, the upstream server is the remote desktop server.",
    ),
    "768": (
        "CLIENT_BAD_REQUEST",
        "The parameters of the request are illegal or otherwise invalid.",
    ),
    "769": (
        "CLIENT_UNAUTHORIZED",
        "Permission was denied, because the user is not logged in. Note that the user may be logged into Guacamole, but still not logged in with respect to the remote desktop server.",
    ),
    "771": (
        "CLIENT_FORBIDDEN",
        "Permission was denied, and logging in will not solve the problem.",
    ),
    "776": (
        "CLIENT_TIMEOUT",
        "The client (usually the user of Guacamole or their browser) is taking too long to respond.",
    ),
    "781": (
        "CLIENT_OVERRUN",
        "The client has sent more data than the protocol allows.",
    ),
    "783": (
        "CLIENT_BAD_TYPE",
        "The client has sent data of an unexpected or illegal type.",
    ),
    "797": (
        "CLIENT_TOO_MANY",
        "The client is already using too many resources. Existing resources must be freed before further requests are allowed.",
    ),
}


class Instruction:
    INSTRUCTION_DELIMITER = ";"
    ELEMENT_SEPERATOR = ","
    LENGTH_SEPERATOR = "."

    def __init__(self, opcode, *args):
        self.opcode = opcode
        self.args = args

    def __str__(self):
        return self.encode_instruction(self.opcode, *self.args)

    @classmethod
    def encode_instruction(cls, *args):
        return (
            cls.ELEMENT_SEPERATOR.join(
                [f"{len(str(x))}{cls.LENGTH_SEPERATOR}{x}" for x in args]
            )
            + cls.INSTRUCTION_DELIMITER
        )

    @classmethod
    def from_string(cls, instruction_string):
        elements = []
        while instruction_string:
            assert instruction_string[0] not in [
                cls.ELEMENT_SEPERATOR,
                cls.INSTRUCTION_DELIMITER,
            ]
            position = instruction_string.find(cls.LENGTH_SEPERATOR)
            length = int(instruction_string[:position])
            assert instruction_string[position] == cls.LENGTH_SEPERATOR
            start = position + 1
            end = start + length + 1
            element = instruction_string[start:end]
            assert element[-1] in [
                cls.ELEMENT_SEPERATOR,
                cls.INSTRUCTION_DELIMITER,
            ], element
            assert length == len(element[:-1])
            elements.append(element[:-1])
            instruction_string = instruction_string[end:]

        return cls(elements[0], *elements[1:])

    @property
    def error(self):
        return self.opcode == "error"

    @property
    def error_code(self):
        if self.error:
            return self.args[-1]

    @property
    def short_description(self):
        if self.error_code:
            return ERROR_MAP[self.error_code][0]

    @property
    def description(self):
        if self.error_code:
            return ERROR_MAP[self.error_code][1]


class Connect(Instruction):
    def __init__(self, args, config):
        args = [args[0]] + [config.get(x, "") for x in args[1:]]
        super().__init__("connect", *args)
