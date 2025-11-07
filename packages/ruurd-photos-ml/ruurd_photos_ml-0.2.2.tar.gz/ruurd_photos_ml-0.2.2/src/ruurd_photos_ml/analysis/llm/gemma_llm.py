from functools import lru_cache

import torch
from transformers import AutoTokenizer, Gemma3ForCausalLM, PreTrainedTokenizer

from .protocol import ChatMessage, LLMProtocol

MAX_NEW_TOKENS = 512
MAX_CONTEXT_TOKENS = 4096


@lru_cache
def get_model_and_tokenizer() -> tuple[Gemma3ForCausalLM, PreTrainedTokenizer]:
    """Retrieve and cache the Gemma-3-4B-it model and tokenizer.

    Returns:
        A tuple containing the Gemma model and its tokenizer.
    """
    model_name = "google/gemma-3-4b-it"
    tokenizer = AutoTokenizer.from_pretrained(model_name)  # type: ignore[no-untyped-call]
    model = Gemma3ForCausalLM.from_pretrained(
        model_name,
        dtype=torch.bfloat16,
        device_map="auto",
    )
    model.eval()
    return model, tokenizer


class GemmaLLM(LLMProtocol):
    """LLM implementation for the Gemma 3 4B instruction-tuned model.

    This class provides methods for both single-turn text generation
    and conversational chat, leveraging the Hugging Face transformers library.
    """

    _system_prompt: str | None = None

    def set_system_prompt(self, system_prompt: str | None) -> None:
        """Set the system prompt for the conversation."""
        self._system_prompt = system_prompt

    def generate(self, prompt: str) -> str:
        """Generates a text response for a single, stateless prompt.

        Args:
            prompt: The input text to the model.

        Returns:
            The generated text response as a string.
        """
        return self.chat(
            [
                ChatMessage(role="user", content=prompt),
            ]
        )

    def chat(self, messages: list[ChatMessage]) -> str:
        """Generates a response for a conversational chat history.

        Args:
            messages: A list of ChatMessage objects representing the conversation history.

        Returns:
            The generated text response from the assistant.
        """
        model, tokenizer = get_model_and_tokenizer()

        # By default, use the original messages list
        processed_messages = messages

        # If a system prompt is set and there are messages, prepend it to the first message.
        if self._system_prompt and messages:
            # Create a shallow copy of the messages list to avoid modifying the original
            processed_messages = list(messages)

            # Create a copy of the first message dictionary to avoid side effects
            first_message = processed_messages[0].copy()

            # Prepend the system prompt to the content of the copied first message
            first_message["content"] = f"{self._system_prompt}\n\n{first_message['content']}"

            # Replace the first message in our new list with the modified copy
            processed_messages[0] = first_message

        prompt = tokenizer.apply_chat_template(
            processed_messages,  # type: ignore[arg-type]
            tokenize=False,
            add_generation_prompt=True,
        )

        # Encode the formatted prompt
        input_ids = tokenizer(
            prompt,
            return_tensors="pt",
            truncation=True,
            max_length=MAX_CONTEXT_TOKENS - MAX_NEW_TOKENS,
        ).to(model.device)

        # Generate a response
        with torch.inference_mode():
            pad_token_id = tokenizer.pad_token_id or tokenizer.eos_token_id
            outputs = model.generate(
                **input_ids,
                max_new_tokens=MAX_NEW_TOKENS,
                do_sample=True,
                temperature=0.7,
                top_k=50,
                top_p=0.95,
                pad_token_id=pad_token_id,
                min_new_tokens=1,
            )
        # Decode the full output and extract only the newly generated part
        input_len = input_ids["input_ids"].shape[-1]

        # Decode only the newly generated tokens
        decoded = tokenizer.decode(outputs[0][input_len:], skip_special_tokens=True)
        return decoded.strip()
