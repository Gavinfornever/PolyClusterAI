import asyncio
import threading
import time
from typing import List
from fastapi import FastAPI, Request, BackgroundTasks
from fastapi.responses import StreamingResponse, JSONResponse
import requests
import os
import sys

parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
# 将上一层目录添加到 sys.path
sys.path.append(parent_dir)

from utils import pretty_print_semaphore, build_logger

WORKER_HEART_BEAT_INTERVAL = 30

worker = None
logger = None

app = FastAPI()


def heart_beat_worker(obj):
    while True:
        time.sleep(WORKER_HEART_BEAT_INTERVAL)
        obj.send_heart_beat()


class BaseModelWorker:
    def __init__(
        self,
        log,
        controller_addr: str,
        worker_addr: str,
        worker_id: str,
        model_path: str,
        model_names: List[str],
        limit_worker_concurrency: int,
        conv_template: str = None,
    ):
        global logger, worker
        logger = log

        self.controller_addr = controller_addr
        self.worker_addr = worker_addr
        self.worker_id = worker_id
        if model_path.endswith("/"):
            model_path = model_path[:-1]
        self.model_names = model_names or [model_path.split("/")[-1]]
        self.limit_worker_concurrency = limit_worker_concurrency
        # self.conv = self.make_conv_template(conv_template, model_path)
        # self.conv.sep_style = int(self.conv.sep_style)
        self.template = conv_template
        
        self.tokenizer = None
        self.context_len = None
        self.call_ct = 0
        self.semaphore = None

        self.heart_beat_thread = None

        # if logger is None:
        #     logger = build_logger("model_worker", f"model_worker_{self.worker_id}.log")
        if worker is None:
            worker = self

    # def make_conv_template(
    #     self,
    #     conv_template: str = None,
    #     model_path: str = None,
    # ) -> Conversation:
    #     """
    #     can be overrided to costomize the conversation template for different model workers.
    #     """
    #     from fastchat.conversation import get_conv_template
    #     from fastchat.model.model_adapter import get_conversation_template

    #     if conv_template:
    #         conv = get_conv_template(conv_template)
    #     else:
    #         conv = get_conversation_template(model_path)
    #     return conv

    def init_heart_beat(self):
        self.register_to_controller()
        self.heart_beat_thread = threading.Thread(
            target=heart_beat_worker,
            args=(self,),
            daemon=True,
        )
        self.heart_beat_thread.start()

    def register_to_controller(self):
        logger.info("Register to controller")

        url = self.controller_addr + "/register_worker"
        data = {
            "worker_name": self.worker_addr,
            "check_heart_beat": True,
            "worker_status": self.get_status(),
        }
        r = requests.post(url, json=data)
        assert r.status_code == 200

    def send_heart_beat(self):
        logger.info(
            f"Send heart beat. Models: {self.model_names}. "
            f"Semaphore: {pretty_print_semaphore(self.semaphore)}. "
            f"call_ct: {self.call_ct}. "
            f"worker_id: {self.worker_id}. "
        )

        url = self.controller_addr + "/receive_heart_beat"

        while True:
            try:
                ret = requests.post(
                    url,
                    json={
                        "worker_name": self.worker_addr,
                        "queue_length": self.get_queue_length(),
                    },
                    timeout=5,
                )
                exist = ret.json()["exist"]
                break
            except (requests.exceptions.RequestException, KeyError) as e:
                logger.error(f"heart beat error: {e}")
            time.sleep(5)

        if not exist:
            self.register_to_controller()

    def get_queue_length(self):
        if (
            self.semaphore is None
            or self.semaphore._value is None
            or self.semaphore._waiters is None
        ):
            return 0
        else:
            return (
                self.limit_worker_concurrency
                - self.semaphore._value
                + len(self.semaphore._waiters)
            )

    def get_status(self):
        return {
            "model_names": self.model_names,
            "speed": 1,
            "queue_length": self.get_queue_length(),
        }

    def count_token(self, params):
        prompt = params["prompt"]

        try:
            input_ids = self.tokenizer(prompt).input_ids
            input_echo_len = len(input_ids)
        except TypeError:
            input_echo_len = self.tokenizer.num_tokens(prompt)

        ret = {
            "count": input_echo_len,
            "error_code": 0,
        }
        return ret

    def get_conv_template(self):
        return {"conv": self.conv}

    def generate_stream_gate(self, params):
        raise NotImplementedError

    def generate_gate(self, params):
        raise NotImplementedError

    def get_embeddings(self, params):
        raise NotImplementedError
