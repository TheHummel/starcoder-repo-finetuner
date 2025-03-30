import os
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
from tqdm import tqdm
import json


current_path = os.path.dirname(os.path.abspath(__file__))
model_path = os.path.join(current_path, "../models/starcoder_3b_local")
tokenizer = AutoTokenizer.from_pretrained(model_path, padding_side="left")
tokenizer.pad_token = tokenizer.eos_token
model = AutoModelForCausalLM.from_pretrained(
    model_path, torch_dtype=torch.float16, device_map="cpu"
)
print("Model loaded!")


def generate_code(prompt: str, max_length: int = 20) -> str:
    inputs = tokenizer(prompt, return_tensors="pt", padding=True, truncation=True)
    outputs = model.generate(
        inputs["input_ids"],
        attention_mask=inputs["attention_mask"],
        max_new_tokens=max_length,
        num_return_sequences=1,
        do_sample=True,
        temperature=0.7,
    )
    full_generated = tokenizer.decode(outputs[0], skip_special_tokens=True).strip()
    return full_generated


def generate_outputs(inputs_path: str) -> list[dict]:
    if not os.path.exists(inputs_path):
        raise FileNotFoundError(f"File not found: {inputs_path}")

    results = []

    for root, _, files in os.walk(inputs_path):
        for file in tqdm(files, desc="Generating outputs", total=len(files)):
            if not file.endswith(".txt"):
                continue
            with open(os.path.join(root, file), "r", encoding="utf-8") as f:
                text = f.read()
                input_text, target = text.split("Output: ")
                input_text = input_text.replace("Input: ", "").strip()
            # print(f"Prompt: {input_text}")
            output = generate_code(input_text)
            # print(f"Output: {output}")
            # print()

            results.append({"prompt": input_text, "output": output, "target": target})

    output_path = os.path.join(current_path, "outputs.json")
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)
    print(f"Results saved to {output_path}")

    return results


if __name__ == "__main__":
    input_path = os.path.join(current_path, "..", "data", "evaluation", "snippets")
    generate_outputs(input_path)
