from typing import cast

from pydantic import Field
from sinapsis_chatbots_base.helpers.llm_keys import LLMChatKeys
from sinapsis_chatbots_base.helpers.postprocess_text import postprocess_text
from sinapsis_chatbots_base.helpers.tags import Tags
from sinapsis_chatbots_base.templates.llm_text_completion_base import (
    LLMCompletionArgs,
    LLMInitArgs,
    LLMTextCompletionAttributes,
    LLMTextCompletionBase,
)
from sinapsis_core.data_containers.data_packet import DataContainer, TextPacket
from sinapsis_core.template_base.base_models import TemplateAttributeType
from sinapsis_core.utils.env_var_keys import SINAPSIS_CACHE_DIR
from transformers import AutoProcessor, Llama4ForConditionalGeneration

LLama4TextToTextUIProperties = LLMTextCompletionBase.UIProperties
LLama4TextToTextUIProperties.tags.extend([Tags.CONVERSATIONAL, Tags.LLAMA, Tags.TEXT_TO_TEXT])


class LLamaMultiModalKeys(LLMChatKeys):
    """Keys for specific Llama format for chat template.

    Keys:
        type (str): key for type
        text (str): key for text
        image (str): key for image
        video (str): key for video
    """

    type: str = "type"
    text: str = "text"
    image: str = "image"
    video: str = "video"


class LLaMA4CompletionArgs(LLMCompletionArgs):
    """Base arguments for controlling LLM text generation (sampling).

    Attributes:
        temperature (float): Controls randomness. 0.0 = deterministic, >0.0 = random. Defaults to `0.2`.
        top_p (float): Nucleus sampling. Considers tokens with cumulative probability >= top_p. Defaults to `0.95`.
        top_k (int): Top-k sampling. Considers the top 'k' most probable tokens. Defaults to `40`.
        max_length (int): The maximum length of the sequence (prompt + generation). Defaults to `20`.
        max_new_tokens (int | None): The maximum number of *new* tokens to generate, excluding the prompt. Defaults to
            `None`.
        do_sample (bool): Whether to use sampling (True) or greedy decoding (False). Defaults to `True`.
        min_p (float | None): Min-p sampling. Filters tokens below this probability threshold. Defaults to `None`.
        repetition_penalty (float): Penalty applied to repeated tokens (1.0 = no penalty). Defaults to `1.0`.
    """

    max_length: int = 20
    max_new_tokens: int | None = None
    do_sample: bool = True
    min_p: float | None = None
    repetition_penalty: float = 1.0


class LLaMA4InitArgs(LLMInitArgs):
    """Initialization arguments for loading a Transformers Llama 4 model.

    Inherits 'llm_model_name' from the base class.

    Attributes:
        llm_model_name (str): The name or path of the LLM model to use
                            (e.g., 'meta-llama/Llama-4-Scout-17B-16E-Instruct').
        cache_dir (str): Path to use for the model cache and download. Defaults to `SINAPSIS_CACHE_DIR`.
        device_map (str): Device mapping for `from_pretrained`. Defaults to `auto`.
        torch_dtype (str | None): Model tensor precision (e.g., 'auto', 'float16'). Defaults to `auto`.
        max_memory (dict | None): Max memory allocation per device. Defaults to `None`.
    """

    cache_dir: str = SINAPSIS_CACHE_DIR
    device_map: str = "auto"
    torch_dtype: str | None = "auto"
    max_memory: dict | None = None


class LLama4TextToText(LLMTextCompletionBase):
    """Template for text-to-text chat processing using the LLama 4 model.

    This template provides support for text-to-text
    conversational chatbots and all the LLama4 models for Scout and Maverick versions.

    Usage example:

    agent:
      name: my_test_agent
    templates:
    - template_name: InputTemplate
      class_name: InputTemplate
      attributes: {}
    - template_name: LLama4
      class_name: LLama4TextToText
      template_input: InputTemplate
      attributes:
        init_args:
          llm_model_name: "meta-llama/Llama-4-Scout-17B-16E-Instruct"
          device_map: auto
          torch_dtype: auto
          max_memory:
            0: "8GiB"
            cpu: "10GiB"
        completion_args:
          max_new_tokens: 256
        role: assistant
        system_prompt: You are an AI and Python expert, and you should reason in every response you provide
        chat_format: chatml
        pattern: null
        keep_before: true
    """

    UIProperties = LLama4TextToTextUIProperties

    class AttributesBaseModel(LLMTextCompletionAttributes):
        """Configuration attributes for LLM-based text completion templates.

        Attributes:
            init_args (LLaMA4InitArgs): LLaMA4 model arguments, including the 'llm_model_name'.
            completion_args (LLaMA4CompletionArgs): LLaMA4 generation arguments, including
                'max_new_tokens', 'temperature', 'top_p', and 'top_k'.
            chat_history_key (str | None): Key in the packet's generic_data to find
                the conversation history.
            rag_context_key (str | None): Key in the packet's generic_data to find
                RAG context to inject.
            system_prompt (str | Path | None): The system prompt (or path to one)
                to instruct the model.
            pattern (str | None): A regex pattern used to post-process the model's response.
            keep_before (bool): If True, keeps text before the 'pattern' match; otherwise,
                keeps text after.
        """

        init_args: LLaMA4InitArgs
        completion_args: LLaMA4CompletionArgs = Field(default_factory=LLaMA4CompletionArgs)

    def __init__(self, attributes: TemplateAttributeType) -> None:
        super().__init__(attributes)
        self.processor = AutoProcessor.from_pretrained(
            self.attributes.init_args.llm_model_name, cache_dir=self.attributes.init_args.cache_dir
        )

    def init_llm_model(self) -> Llama4ForConditionalGeneration:
        """Uses LLama4ForConditionalGeneration to initialize a pretrained model with the corresponding memory."""
        model = Llama4ForConditionalGeneration.from_pretrained(
            self.attributes.init_args.llm_model_name,
            **self.attributes.init_args.model_dump(exclude={"llm_model_name"}),
        )
        return model

    def infer(self, text: str | list) -> str | None:
        """Specific method to apply a chat template before using the get_response method.

        Args:
            text (str | list): text to be processed by the llm
        Returns:
            str | None: If a response is generated by the llm, it returns the processed string
        """
        inputs = self.processor.apply_chat_template(
            text, add_generation_prompt=True, tokenize=True, return_dict=True, return_tensors="pt"
        ).to(self.llm.device)
        response = self.get_response(inputs)
        return response

    @staticmethod
    def extract_additional_content(container: DataContainer) -> list:
        """Extracts additional content from the container.

        This base implementation returns an empty list. Subclasses (like multimodal ones)
        should override this to extract relevant data.

        Args:
            container (DataContainer): The container holding potential extra data.

        Returns:
            list: A list of dictionaries representing the additional content items
                  (e.g., image data formatted for the model).
        """
        _ = container
        return []

    def generate_response(self, container: DataContainer) -> DataContainer:
        """Method to generate the response, by adding to the inference any provided context or content.

        Args:
            container (DataContainer): Input DataContainer with packet or packets to be processed

        Returns:
            DataContainer: The DataContainer with a text response for each of the input text packets
        """
        self.logger.debug("Chatbot in progress")
        responses: list[TextPacket] = []

        for packet in container.texts:
            full_context = []
            user_content = []
            user_id, session_id, prompt = self.prepare_conversation_context(packet)
            user_content.extend(self.extract_additional_content(container=container))

            if self.system_prompt:
                system_prompt = [
                    {LLamaMultiModalKeys.type: LLamaMultiModalKeys.text, LLamaMultiModalKeys.text: self.system_prompt}
                ]
                system_prompt_msg = self.generate_dict_msg(LLMChatKeys.system_value, system_prompt)
                full_context.append(system_prompt_msg)

            if self.attributes.chat_history_key:
                full_context.extend(packet.generic_data.get(self.attributes.chat_history_key, []))

            user_content.append({LLamaMultiModalKeys.type: LLamaMultiModalKeys.text, LLamaMultiModalKeys.text: prompt})
            user_prompt_message = self.generate_dict_msg(LLMChatKeys.user_value, user_content)
            full_context.append(user_prompt_message)
            response = self.infer(full_context)
            self.logger.debug("End of interaction.")
            if response:
                responses.append(TextPacket(source=session_id, content=response, id=user_id))

        container.texts.extend(responses)
        return container

    def get_response(self, input_message: str | list | dict) -> str | None:
        """Specific method to get the response using the generate method for the llm model.

        It unwraps the input message that comes as a dictionary, and returns the response as a dictionary,
        to be post-processed and returns a string with the model response.

        Args:
            input_message (str | list | dict): Dictionary with the input message to be passed to the
            generate method
        Returns:
            the response as a string after being post-processed.
        """
        input_message = cast(dict, input_message)
        response = self.llm.generate(**input_message, **self.attributes.completion_args.model_dump(exclude_none=True))
        input_len = input_message.get("input_ids", None)
        if input_len is not None:
            input_len = input_len.shape[-1]
        new_tokens = response[:, input_len:]
        response = self.processor.batch_decode(new_tokens)[0]
        if response:
            response = postprocess_text(str(response), self.attributes.pattern, self.attributes.keep_before)
            return response
        return None
