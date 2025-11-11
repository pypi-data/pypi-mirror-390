import asyncio
from collections.abc import AsyncGenerator
from copy import deepcopy

from sinapsis_chatbots_base.helpers.llm_keys import LLMChatKeys, MCPKeys
from sinapsis_core.data_containers.data_packet import DataContainer, TextPacket
from sinapsis_core.utils.sentinels import SENTINEL_GENERIC_KEY, SINAPSIS_END_OF_STREAM

from sinapsis_llama_cpp.helpers.llama_keys import LLaMAModelKeys
from sinapsis_llama_cpp.templates.llama_text_completion import LLaMATextCompletion


class StreamingLLaMATextCompletion(LLaMATextCompletion):
    """A streaming version of the LLaMATextCompletion template.

    Inherits initialization and basic configuration from LLaMATextCompletion,
    but overrides response generation to use async streaming.

    Usage example:

    agent:
      name: my_test_agent
    templates:
    - template_name: InputTemplate
      class_name: InputTemplate
      attributes: {}
    - template_name: LLaMATextCompletion
      class_name: LLaMATextCompletion
      template_input: InputTemplate
      attributes:
        init_args:
          llm_model_name: 'TheBloke/Mistral-7B-Instruct-v0.2-GGUF'
          llm_model_file: 'mistral-7b-instruct-v0.2.Q2_K.gguf'
          n_gpu_layers: -1
          use_mmap: true
          use_mlock: false
          seed: 42
          n_ctx: 8192
          n_batch: 512
          n_ubatch: 512
          n_threads: null
          n_threads_batch: null
          flash_attn: true
          chat_format: null
          verbose: true
        completion_args:
          temperature: 0.2
          top_p: 0.95
          top_k: 40
          max_tokens: 4096
          min_p: 0.05
          stop: null
          seed: 42
          repeat_penalty: 1.0
          presence_penalty: 0.0
          frequency_penalty: 0.0
          logit_bias: null
        chat_history_key: null
        rag_context_key: null
        system_prompt: You are an expert in AI.
        pattern: null
        keep_before: true
    """

    IS_STREAMING = True

    async def _stream_responses(self, input_message: str | list) -> AsyncGenerator[str, None]:
        """Creates and iterates over a streaming chat completion response.

        Args:
            input_message (Union[str, List]): The formatted list of messages for the LLM.

        Returns:
            AsyncGenerator[str, None]: An asynchronous generator yielding text chunks.

        Yields:
            str: Individual text chunks received from the model's streaming response.
        """
        completion_args = self.attributes.completion_args.model_dump(exclude_none=True)
        completion_args["stream"] = True

        for chat_completion_chunk in await asyncio.to_thread(
            self.llm.create_chat_completion, messages=input_message, **completion_args
        ):
            if (
                LLMChatKeys.choices in chat_completion_chunk
                and len(chat_completion_chunk[LLMChatKeys.choices]) > 0
                and LLaMAModelKeys.delta in chat_completion_chunk[LLMChatKeys.choices][0]
                and LLMChatKeys.content in chat_completion_chunk[LLMChatKeys.choices][0][LLaMAModelKeys.delta]
            ):
                chunk_text = chat_completion_chunk[LLMChatKeys.choices][0][LLaMAModelKeys.delta][LLMChatKeys.content]
                if chunk_text:
                    self.logger.debug(f"Yielding chunk: '{chunk_text}'")
                    yield chunk_text

            if (
                LLMChatKeys.choices in chat_completion_chunk
                and len(chat_completion_chunk[LLMChatKeys.choices]) > 0
                and MCPKeys.finish_reason in chat_completion_chunk[LLMChatKeys.choices][0]
                and chat_completion_chunk[LLMChatKeys.choices][0][MCPKeys.finish_reason] is not None
            ):
                self.logger.debug(
                    f"Stream finished. Reason: {chat_completion_chunk[LLMChatKeys.choices][0][MCPKeys.finish_reason]}"
                )
                break

            await asyncio.sleep(0)

    async def get_response(self, input_message: str | list) -> AsyncGenerator[str, None]:
        """Asynchronously gets streaming response chunks, handling potential errors and retries.

        Args:
            input_message (Union[str, List]): The input messages list for the LLM.

        Returns:
            AsyncGenerator[str, None]: An asynchronous generator yielding text chunks.

        Yields:
            str: Text chunks from the streaming response.
        """
        self.logger.debug(f"Query is {input_message}")
        try:
            async for chunk in self._stream_responses(input_message):
                yield chunk
        except (IndexError, AttributeError):
            self.reset_llm_state()
            if self.llm:
                async for chunk in self._stream_responses(input_message):
                    yield chunk

    async def generate_response(self, container: DataContainer) -> AsyncGenerator[DataContainer, None]:
        """Builds context and yields partial DataContainers for each response chunk.

        Args:
            container (DataContainer): The input container with text packets.

        Returns:
            AsyncGenerator[DataContainer, None]: An asynchronous generator yielding DataContainers.

        Yields:
            DataContainer: Partial containers with one response chunk each, then the final container with EOS sentinel.
        """
        for packet in container.texts:
            full_context = []
            user_id, session_id, prompt = self.prepare_conversation_context(packet)
            if self.system_prompt:
                system_prompt_msg = self.generate_dict_msg(LLMChatKeys.system_value, self.system_prompt)
                full_context.append(system_prompt_msg)

            if self.attributes.chat_history_key:
                full_context.extend(packet.generic_data.get(self.attributes.chat_history_key, []))

            message = self.generate_dict_msg(LLMChatKeys.user_value, prompt)
            full_context.append(message)

            async for response_chunk in self.get_response(full_context):
                if not response_chunk:
                    break
                partial_container: DataContainer = deepcopy(container)

                partial_container.texts.append(TextPacket(source=session_id, content=response_chunk, id=user_id))
                yield partial_container

        # add sentinel
        container.generic_data[SENTINEL_GENERIC_KEY] = SINAPSIS_END_OF_STREAM
        yield container

    async def async_execute(self, container: DataContainer) -> AsyncGenerator[DataContainer, None]:
        """Asynchronously executes the streaming generation process.

        Args:
            container (DataContainer): The input data container.

        Returns:
            AsyncGenerator[DataContainer, None]: An asynchronous generator yielding DataContainers.

        Yields:
            DataContainer: Partial containers with response chunks, followed by
                           the final container (potentially with error info).
        """
        try:
            async for partial_container in self.generate_response(container):
                yield partial_container
        except (IndexError, TypeError) as e:
            self.logger.error(f"got error when stopping {e}")
