import torch

from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline
from transformers import BitsAndBytesConfig
from langchain.llms import HuggingFacePipeline
from langchain.llms import HuggingFaceHub

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
    # Access token
    HF_TOKEN = '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'
    
    # Define additional generation parameters, such as sampling temperature.
    gen_kwargs = {
        'temperature': kwargs.get('temperature', 0.5),
        'max_new_tokens': kwargs.get('max_new_tokens', max_new_tokens)
    }
    
    # create llm model
    llm = HuggingFaceHub(
        repo_id=model_name,
        model_kwargs=gen_kwargs,
        huggingfacehub_api_token=HF_TOKEN
    )

    return llm