import os
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig
from dotenv import load_dotenv


def load_model(model_path: str) -> None:

    if not os.path.exists(model_path):
        raise FileNotFoundError(f"File not found: {model_path}")

    tokenizer = AutoTokenizer.from_pretrained(model_path, padding_side="left")
    tokenizer.pad_token = tokenizer.eos_token
    model = AutoModelForCausalLM.from_pretrained(
        model_path, torch_dtype=torch.float16, device_map="cpu"
    )
    print("Model loaded!")

    return model, tokenizer


def load_model_from_hf(
    model_name: str = "bigcode/starcoderbase-3b",
    save_path: str = "./models/starcoder_3b_local",
    quant_config: BitsAndBytesConfig = BitsAndBytesConfig(
        load_in_4bit=True,
        bnb_4bit_compute_dtype=torch.float16,
        bnb_4bit_use_double_quant=True,
    ),
) -> None:
    load_dotenv()
    hf_token = os.getenv("HF_TOKEN")
    if not hf_token:
        raise ValueError("HF_TOKEN not found in .env file. Please add it.")

    try:
        print("Downloading tokenizer...")
        tokenizer = AutoTokenizer.from_pretrained(model_name, token=hf_token)

        print("Downloading and loading model...")
        if torch.cuda.is_available():
            print("CUDA detected, using GPU quantization...")
            model = AutoModelForCausalLM.from_pretrained(
                model_name,
                quantization_config=quant_config,
                device_map="auto",
                token=hf_token,
            )
        else:
            print("No CUDA detected, falling back to CPU (full precision)...")
            model = AutoModelForCausalLM.from_pretrained(
                model_name, torch_dtype=torch.float16, device_map="cpu", token=hf_token
            )

        print("Model loaded successfully!")
        print(f"Model memory footprint: {model.get_memory_footprint() / 1e9:.2f} GB")

        print(f"Saving to {save_path}...")
        tokenizer.save_pretrained(save_path)
        model.save_pretrained(save_path)
        print("Saved successfully!")

    except Exception as e:
        print(f"Error: {e}")

    return model, tokenizer
