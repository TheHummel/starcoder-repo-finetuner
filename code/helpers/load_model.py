import os
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer


def load_model(model_path):

    if not os.path.exists(model_path):
        raise FileNotFoundError(f"File not found: {model_path}")

    tokenizer = AutoTokenizer.from_pretrained(model_path, padding_side="left")
    tokenizer.pad_token = tokenizer.eos_token
    model = AutoModelForCausalLM.from_pretrained(
        model_path, torch_dtype=torch.float16, device_map="cpu"
    )
    print("Model loaded!")

    return model, tokenizer
