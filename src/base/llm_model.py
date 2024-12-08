import torch

from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline
from transformers import BitsAndBytesConfig
from langchain.llms import HuggingFacePipeline

model_name: str = 'microsoft/phi-2'
model = AutoModelForCausalLM.from_pretrained(
    model_name,
    low_cpu_mem_usage=True
)

def get_hf_llm(model_name: str = "microsoft/phi-2", max_new_tokens = 1024, **kwargs):
    """
    Creates and returns a HuggingFace LLM pipeline for text generation.

    Args:
        model_name (str): The name of the pre-trained model to load from the HuggingFace model hub.
                         Defaults to "microsoft/phi-2".
        max_new_tokens (int): The maximum number of tokens to generate in the output sequence.
                              Defaults to 1024.
        **kwargs: Additional keyword arguments that can be passed to customize the model or tokenizer.

    Returns:
        llm: A HuggingFacePipeline instance configured for text generation.
    """
    # Load a pre-trained causal language model with low memory usage optimization for CPUs.
    model = AutoModelForCausalLM.from_pretrained(
        model_name,
        low_cpu_mem_usage=True
    )
    # Load the tokenizer corresponding to the specified model.
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    # Create a text-generation pipeline using the model and tokenizer.
    model_pipeline = pipeline(
        'text-generation',
        model=model,
        tokenizer=tokenizer,
        max_new_tokens=max_new_tokens,
        pad_token_id=tokenizer.eos_token_id,
        device_map='cpu'
    )
    # Define additional generation parameters, such as sampling temperature.
    gen_kwargs = {
        'temperature': 0.5
    }
    # Wrap the pipeline in a HuggingFacePipeline object for further use.
    llm = HuggingFacePipeline(
        pipeline=model_pipeline,
        model_kwargs=gen_kwargs
    )

    return llm