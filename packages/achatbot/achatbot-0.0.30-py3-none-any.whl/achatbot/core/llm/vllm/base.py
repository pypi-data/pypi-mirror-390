from abc import abstractmethod
import logging
import os
from queue import Queue
from typing import AsyncGenerator, Iterator
from concurrent.futures import ThreadPoolExecutor
import uuid

import numpy as np
from PIL import Image

try:
    from transformers import AutoTokenizer
    from vllm import LLM, AsyncLLMEngine, AsyncEngineArgs, SamplingParams
    from achatbot.types.llm.vllm import VllmEngineArgs, LMGenerateArgs
except ModuleNotFoundError as e:
    logging.error(f"Exception: {e}")
    logging.error("you need to `pip install achatbot[vllm]`")
    raise Exception(f"Missing module: {e}")

from achatbot.common.session import Session
from achatbot.common.chat_history import ChatHistory
from achatbot.common.logger import Logger
from achatbot.common.utils import task
from achatbot.common.types import SessionCtx
from . import VLlmBase


class VllmEngineBase(VLlmBase):
    def __init__(self, **kwargs) -> None:
        super().__init__()
        self.args = VllmEngineArgs(**kwargs)
        self.gen_args = LMGenerateArgs(**self.args.gen_args)
        # https://docs.vllm.ai/en/stable/api/vllm/engine/arg_utils.html#vllm.engine.arg_utils.AsyncEngineArgs.__init__
        self.serv_args = AsyncEngineArgs(**self.args.serv_args)
        logging.info(
            f"server args: {self.serv_args.__dict__} | default generate args: {self.gen_args.__dict__}"
        )
        self.engine = AsyncLLMEngine.from_engine_args(self.serv_args)
        self.tokenizer = AutoTokenizer.from_pretrained(self.serv_args.model)

        self._chat_history = ChatHistory(self.args.chat_history_size)
        if self.args.init_chat_role and self.args.init_chat_prompt:
            self._chat_history.init(
                {
                    "role": self.args.init_chat_role,
                    "content": self.args.init_chat_prompt,
                }
            )

        # subclass to init
        self.init()

    def init(self):
        pass
