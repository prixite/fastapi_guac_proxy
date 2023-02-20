import asyncio
import logging
from guacamole.instruction import Instruction, Connect

logger = logging


class GuacamoleClient:
    VERSION = "VERSION_1_3_0"
    READ_BUFFER_SIZE = 4096

    def __init__(self, host, port, config, debug=False):
        self.host = host
        self.port = port
        self.buffer = ""
        self.client_version = ""
        self.config = config
        self.client_id = None

        if debug:
            logging.getLogger().setLevel(logging.DEBUG)
            logger.debug("Debug mode")

    async def connect(self):
        self.reader, self.writer = await asyncio.open_connection(self.host, self.port)
        logger.info(f"Connection established with {self.host}:{self.port}")

    async def write(self, data):
        self.writer.write(data.encode())
        await self.writer.drain()
        logger.debug(f"Sending: {data}")

    async def read(self):
        index = self.buffer.find(Instruction.INSTRUCTION_DELIMITER)
        while index == -1:
            raw = await self.reader.read(self.READ_BUFFER_SIZE)
            self.buffer += raw.decode()
            index = self.buffer.find(Instruction.INSTRUCTION_DELIMITER)

        raw_instruction = self.buffer[: index + 1]
        assert raw_instruction[-1] == Instruction.INSTRUCTION_DELIMITER
        instruction = Instruction.from_string(raw_instruction)
        self.buffer = self.buffer[len(str(instruction)) :]
        logger.debug(f"Received: {instruction}")
        return instruction

    async def close(self):
        self.writer.close()
        await self.writer.wait_closed()
        logger.info("Connection closed")

    async def send(self, instruction):
        await self.write(str(instruction))

    async def send_batch(self, instructions):
        await self.write("".join([str(x) for x in instructions]))

    async def handshake(self):
        await self.send_batch(
            [
                Instruction("select", self.config["protocol"]),
                Instruction("size", *self.config["size"]),
                Instruction("audio", *self.config["audio"]),
                Instruction("video", *self.config["video"]),
                Instruction("image", *self.config["image"]),
            ]
        )
        instruction = await self.read()
        assert instruction.opcode == "args"
        await self.send(Connect(instruction.args, self.config["args"]))
        instruction = await self.read()
        assert instruction.opcode == "ready"
        self.client_id = instruction.args[0]
