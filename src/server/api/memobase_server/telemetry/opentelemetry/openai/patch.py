from .instruments import Instruments
from .utils import response_as_dict, openai_tokens, record_metrics
import time
import logging

LOG = logging.getLogger(__name__)

def chat_completions(instrument: Instruments, deployment_environment: str):
    class TracedSyncStream:
        def __init__(self, wrapped, kwargs):
            self.__wrapped__ = wrapped
            # Placeholder for aggregating streaming response
            self._llmresponse = ""
            self._response_id = ""
            self._response_model = ""
            self._finish_reason = ""
            self._openai_response_service_tier = ""
            self._openai_system_fingerprint = ""

            self._kwargs = kwargs
            self._start_time = time.time()
            self._end_time = None

        def __enter__(self):
            self.__wrapped__.__enter__()
            return self
        
        def __exit__(self, exc_type, exc_value, traceback):
            self.__wrapped__.__exit__(exc_type, exc_value, traceback)

        def __iter__(self):
            return self
        
        def __getattr__(self, name):
            return getattr(self.__wrapped__, name)
        
        def __next__(self):
            try:
                chunk = self.__wrapped__.__next__()

                chunked = response_as_dict(chunk)
                # Collect message IDs and aggregated response from events
                if (len(chunked.get('choices')) > 0 and ('delta' in chunked.get('choices')[0] and
                    'content' in chunked.get('choices')[0].get('delta'))):

                    content = chunked.get('choices')[0].get('delta').get('content')
                    if content:
                        self._llmresponse += content
                self._response_id = chunked.get('id')
                self._response_model = chunked.get('model')
                self._finish_reason = chunked.get('choices')[0].get('finish_reason')
                self._openai_response_service_tier = chunked.get('service_tier')
                self._openai_system_fingerprint = chunked.get('system_fingerprint')
                return chunk

            except StopIteration:
                self._end_time = time.time()
                # Format 'messages' into a single string
                message_prompt = self._kwargs.get("messages", "")
                formatted_messages = []
                for message in message_prompt:
                    role = message["role"]
                    content = message["content"]

                    if isinstance(content, list):
                        content_str_list = []
                        for item in content:
                            if item["type"] == "text":
                                content_str_list.append(f'text: {item["text"]}')
                            else:
                                LOG.warning(f"Don't support {item['type']}")
                        content_str = ", ".join(content_str_list)
                        formatted_messages.append(f"{role}: {content_str}")
                    else:
                        formatted_messages.append(f"{role}: {content}")
                prompt = "\n".join(formatted_messages)

                request_model = self._kwargs.get("model", "gpt-4o")
                input_tokens = openai_tokens(prompt,
                                                request_model)
                output_tokens = openai_tokens(self._llmresponse,
                                                    request_model)
                record_metrics(instrument, self._end_time, 
                               self._start_time, input_tokens, output_tokens, 
                               deployment_environment, request_model, self._response_model)
            except Exception as e:
                raise e


    def wrapper(wrapped, instance, args, kwargs):
        streaming = kwargs.get("stream", False)
        request_model = kwargs.get("model", "gpt-4o")
        
        if streaming:
            awaited_wrapped = wrapped(*args, **kwargs)

            return TracedSyncStream(awaited_wrapped, kwargs)
        else:
            start_time = time.time()
            response = wrapped(*args, **kwargs)
            end_time = time.time()

            response_dict = response_as_dict(response)

            input_tokens = response_dict.get('usage').get('prompt_tokens')
            output_tokens = response_dict.get('usage').get('completion_tokens')

            record_metrics(instrument, end_time, start_time, input_tokens, output_tokens, 
                           deployment_environment, request_model, response_dict.get('model'))
            return response

    return wrapper


def async_chat_completions(instrument: Instruments, deployment_environment: str):
    class TracedAsyncStream:
        def __init__(self, wrapped, kwargs):
            self.__wrapped__ = wrapped

            self._llmresponse = ""
            self._response_id = ""
            self._response_model = ""
            self._finish_reason = ""
            self._openai_response_service_tier = ""
            self._openai_system_fingerprint = ""

            self._kwargs = kwargs
            self._start_time = time.time()
            self._end_time = None
        
        async def __aenter__(self):
            await self.__wrapped__.__aenter__()
            return self

        async def __aexit__(self, exc_type, exc_value, traceback):
            await self.__wrapped__.__aexit__(exc_type, exc_value, traceback)

        def __aiter__(self):
            return self

        async def __getattr__(self, name):
            return getattr(await self.__wrapped__, name)

        async def __anext__(self):
            try:
                chunk = await self.__wrapped__.__anext__()
                chunked = response_as_dict(chunk)

                # Collect message IDs and aggregated response from events
                if (len(chunked.get('choices')) > 0 and ('delta' in chunked.get('choices')[0] and
                    'content' in chunked.get('choices')[0].get('delta'))):

                    content = chunked.get('choices')[0].get('delta').get('content')
                    if content:
                        self._llmresponse += content
                self._response_id = chunked.get('id')
                self._response_model = chunked.get('model')
                self._finish_reason = chunked.get('choices')[0].get('finish_reason')
                self._openai_response_service_tier = chunked.get('service_tier')
                self._openai_system_fingerprint = chunked.get('system_fingerprint')
                return chunk

            except StopAsyncIteration:
                self._end_time = time.time()
                # Format 'messages' into a single string
                message_prompt = self._kwargs.get("messages", "")
                formatted_messages = []
                for message in message_prompt:
                    role = message["role"]
                    content = message["content"]

                    if isinstance(content, list):
                        content_str_list = []
                        for item in content:
                            if item["type"] == "text":
                                content_str_list.append(f'text: {item["text"]}')
                            else:
                                LOG.warning(f"Don't support {item['type']}")
                        content_str = ", ".join(content_str_list)
                        formatted_messages.append(f"{role}: {content_str}")
                    else:
                        formatted_messages.append(f"{role}: {content}")
                prompt = "\n".join(formatted_messages)

                request_model = self._kwargs.get("model", "gpt-4o")

                input_tokens = openai_tokens(prompt,
                                                request_model)
                output_tokens = openai_tokens(self._llmresponse,
                                                    request_model)
                record_metrics(instrument, self._end_time, 
                               self._start_time, input_tokens, output_tokens, 
                               deployment_environment, request_model, self._response_model)
            except Exception as e:
                raise e

    async def wrapper(wrapped, instance, args, kwargs):
        streaming = kwargs.get("stream", False)
        request_model = kwargs.get("model", "gpt-4o")

        if streaming:
            awaited_wrapped =  await wrapped(*args, **kwargs)

            return TracedAsyncStream(awaited_wrapped, kwargs)
        else:
            start_time = time.time()
            response = await wrapped(*args, **kwargs)
            end_time = time.time()

            response_dict = response_as_dict(response)

            input_tokens = response_dict.get('usage').get('prompt_tokens')
            output_tokens = response_dict.get('usage').get('completion_tokens')

            record_metrics(instrument, end_time, start_time, input_tokens, output_tokens, 
                           deployment_environment, request_model, response_dict.get('model'))
            return response

    return wrapper

