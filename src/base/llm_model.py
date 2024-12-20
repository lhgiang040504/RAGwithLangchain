import torch
import os

from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline
from transformers import BitsAndBytesConfig
from langchain.llms import HuggingFacePipeline
from langchain.llms import HuggingFaceHub

from langchain_groq import ChatGroq

from dotenv import dotenv_values
config = dotenv_values("../.env")

def get_hf_chatbot_llm(model_name: str = "microsoft/phi-2", call_model_api=True, **kwargs):
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
    # Define additional generation parameters, such as sampling temperature.
    gen_kwargs = {
        'temperature': kwargs.get('temperature', 0.5),
        'max_new_tokens': kwargs.get('max_new_tokens', 1024)
    }

    if call_model_api:
        # create llm model
        llm = HuggingFaceHub(
            repo_id=model_name,
            model_kwargs=gen_kwargs,
            huggingfacehub_api_token=config['HUGGINGFACEHUB_API_TOKEN']
        )
    else:
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
            max_new_tokens=kwargs.get('max_new_tokens', 1024),
            pad_token_id=tokenizer.eos_token_id,
            device_map='auto'
        )
        # Wrap the pipeline in a HuggingFacePipeline object for further use.
        llm = HuggingFacePipeline(
            pipeline=model_pipeline,
            model_kwargs=gen_kwargs
        )

    return llm

def get_gsk_parse_llm(model_name: str = "llama-3.1-70b-versatile", **kwargs):
    """
    Initializes a ChatGroq language model with specified parameters.

    Args:
        model_name (str): Name of the model to initialize.
        **kwargs: Additional parameters to customize the ChatGroq instance.

    Returns:
        ChatGroq: The initialized language model.

    Raises:
        ValueError: If the GROQ_API_KEY is not set in the environment.
    """
    llm = ChatGroq(
        model_name=model_name,
        model_kwargs=kwargs,
        groq_api_key=config['GROQ_API_KEY']
    )
    return llm
