import json
from abc import ABC
from hashlib import md5
from http import HTTPStatus
import httpx
from typing import Callable, Optional

import backoff
from genie_flow_invoker import GenieInvoker
from genie_flow_invoker.utils import get_config_value
from loguru import logger
import ollama
from ollama import Client, GenerateResponse, ChatResponse, EmbedResponse
import yaml


_OLLAMA_CLIENT: Optional[Client] = None


def _get_ollama_client(config) -> Client:
    global _OLLAMA_CLIENT
    if _OLLAMA_CLIENT is None:
        ollama_url = get_config_value(
            config,
            "OLLAMA_URL",
            "ollama_url",
            "URL for the Ollama endpoint",
        )

        _OLLAMA_CLIENT = Client(
            host=ollama_url,
            limits=httpx.Limits(max_connections=1000, max_keepalive_connections=1000),
            timeout=300.0,
        )
        logger.info("Created shared Ollama client for {url}", url=ollama_url)

    return _OLLAMA_CLIENT


class AbstractOllamaInvoker(GenieInvoker, ABC):

    def __init__(
            self,
            ollama_client: Client,
            model: str,
            format: str,
            backoff_max_time: int,
            backoff_max_tries: int,
    ):
        """
        Abstract Ollama invoker.

        :param ollama_client: the Ollama client instance to use
        :param model: the model to pass to Ollama instance
        :param format: the output format to pass to Ollama instance
        :param backoff_max_time: maximum time in seconds to backoff every retry
        :param backoff_max_tries: maximum number of times to backoff
        """
        self.ollama_client = ollama_client
        self.model = model
        self.format = format
        self.backoff_max_time = backoff_max_time
        self.backoff_max_tries = backoff_max_tries

    @classmethod
    def from_config(cls, config: dict) -> "AbstractOllamaInvoker":
        return cls(
            ollama_client=_get_ollama_client(config),
            model=get_config_value(
                config,
                "OLLAMA_MODEL",
                "model",
                "Model to use",
            ),
            format=get_config_value(
                config,
                "OLLAMA_OUTPUT",
                "format",
                "Output format to use",
                "",
            ),
            backoff_max_time = get_config_value(
                config,
                "OLLAMA_BACKOFF_MAX_TIME",
                "backoff_max_time",
                "Max backoff time (seconds)",
                61,
            ),
            backoff_max_tries = get_config_value(
                config,
                "OLLAMA_MAX_BACKOFF_TRIES",
                "backoff_max_tries",
                "Max backoff tries",
                15,
            ),
        )

    def call_with_backoff(self, func: Callable, **kwargs):
        """
        Call a function with a backoff if a Rate limit error occurs.

        :param func: the function to call
        :param kwargs: the keyword arguments to pass to the function
        :return: the result of the function
        """
        def backoff_logger(details: dict):
            logger.info(
                "Backing off {wait:0.1f} seconds after {tries} tries ",
                "for a {cls} invocation",
                **details,
                cls=self.__class__.__name__,
            )

        @backoff.on_exception(
            wait_gen=backoff.fibo,
            max_value=self.backoff_max_time,
            max_tries=self.backoff_max_tries,
            exception=TimeoutError,
            on_backoff=backoff_logger,
        )
        def make_call():
            try:
                result = func(**kwargs)
                logger.debug("Ollama response received", **result.model_dump())
                return result
            except ollama.ResponseError as e:
                logger.error(
                    "Ollama invoker failed with error {error}",
                    error=e.error,
                )
                if e.status_code == HTTPStatus.TOO_MANY_REQUESTS:
                    raise TimeoutError
                raise e

        return make_call()


class OllamaGenerateInvoker(AbstractOllamaInvoker):


    def invoke(self, content: str) -> str:
        
        try:
            prompt_with_images = yaml.safe_load(content)
        except yaml.YAMLError as e:
            logger.debug(
                "Cannot parse the following content as YAML. "
                "Assuming this is a sole user message. '{content}'",
                content=content,
            )
            prompt = content
            images = None
        else:
            prompt = prompt_with_images["prompt"]
            images = prompt_with_images["images"]


        result: GenerateResponse = self.call_with_backoff(
            self.ollama_client.generate,
            model=self.model,
            format=self.format,
            prompt=prompt,
            images=images,
        )

        logger.info(
            "Ollama Generate Invoker completed successfully",
            **result.model_dump(exclude={"response"}),
            response_hash=md5(result.response.encode("utf-8")).hexdigest()
        )
        return result.response


class OllamaChatInvoker(AbstractOllamaInvoker):

    def invoke(self, content: str) -> str:
        try:
            messages = yaml.safe_load(content)
        except yaml.YAMLError as e:
            logger.debug(
                "Cannot parse the following content as YAML. "
                "Assuming this is a sole user message. '{content}'",
                content=content,
            )
            messages = content

        if isinstance(messages, str):
            messages = [dict(role="user", content=messages)]

        for message in messages:
            if message["role"] not in {"system", "user", "assistant"}:
                logger.warning(
                    "Ollama chat invoker received a message with unknown role \"{role}\"; "
                    "changed to role \"user\"",
                    role=message["role"],
                )
                message["role"] = "user"

        result: ChatResponse = self.call_with_backoff(
            self.ollama_client.chat,
            model=self.model,
            format=self.format,
            messages=messages,
        )

        logger.info(
            "Ollama Chat Invoker completed successfully",
            **result.model_dump(exclude={"message"}),
            message_hash=md5(result.message.content.encode('utf-8')).hexdigest(),
        )
        return result.message.content


class OllamaEmbedInvoker(AbstractOllamaInvoker):
    """
    Embedding of the content. If content is JSON-parsable as a list, then
    that list is passed for batch-embedding. In that case, the result will
    also be a list of embeddings. If the content is just a string, then
    only the embedding of that string is returned.
    """

    def invoke(self, content: str) -> str:
        try:
            content_parsed = json.loads(content)
        except json.JSONDecodeError as e:
            content_parsed = content

        result: EmbedResponse = self.call_with_backoff(
            self.ollama_client.embed,
            model=self.model,
            input=content_parsed,
        )
        logger.info(
            "Ollama Embed Invoker completed successfully",
            **result.model_dump(),
        )
        if isinstance(content_parsed, list):
            return json.dumps(result.embeddings)
        return json.dumps(result.embeddings[0])
