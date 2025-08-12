import time
import logging
from src.utils.format import format_dialogue
from src.ipc.file_ipc import init_ipc, read_request, write_response
from src.ipc.service import IpcService
from src.llm.dialogue_generator import DialogueGenerator
from src.codecs.gen3 import Gen3TextCodec
from src.config.settings import Settings

def run_ipc_loop(settings: Settings, generator: DialogueGenerator, codec: Gen3TextCodec) -> None:
    logging.info("IPC Mode Enabled — Atomic IPC handshake")
    service = IpcService.from_settings(settings)
    try:
        while True:
            req = service.read_request()
            if req:
                req_id, original = req
                decoded_original = codec.decode(original)
                formatted_ori = decoded_original.replace("\n", " ").replace("\x0c", " ")
                logging.info(f"[{req_id}] Received: {formatted_ori!r}")

                rewrite = ""
                while len(rewrite.strip()) < 5:
                    rewrite = generator.generate(formatted_ori)

                logging.info(f"[{req_id}] Rewritten: {rewrite!r}")
                rewrite = format_dialogue(rewrite)
                data = codec.encode(rewrite, max_len=255)
                service.write_response(req_id, data)

            time.sleep(0.05)
    except KeyboardInterrupt:
        logging.info("IPC mode terminated by user.")

