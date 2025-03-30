import os
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
from dotenv import load_dotenv
from transformers import BitsAndBytesConfig

load_dotenv()
hf_token = os.getenv("HF_TOKEN")
if not hf_token:
    raise ValueError("HF_TOKEN not found in .env file. Please add it.")

# # Test token
# url = "https://huggingface.co/bigcode/starcoderbase-3b/resolve/main/config.json"
# headers = {"Authorization": f"Bearer {hf_token}"}
# print(f"Testing token with {url}...")
# response = requests.get(url, headers=headers)
# if response.status_code != 200:
#     exit(1)

# Model details
model_name = "bigcode/starcoderbase-3b"
save_path = "./models/starcoder_3b_local"

# Quantization config
quant_config = BitsAndBytesConfig(
    load_in_4bit=True,
    bnb_4bit_compute_dtype=torch.float16,
    bnb_4bit_use_double_quant=True,
)

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
