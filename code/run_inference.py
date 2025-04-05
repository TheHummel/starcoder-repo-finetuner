import os
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
from tqdm import tqdm
import json
import random

from helpers.load_model import load_model


current_path = os.path.dirname(os.path.abspath(__file__))


def run_model(
    model: AutoModelForCausalLM,
    tokenizer: AutoTokenizer,
    prompt: str,
    max_length: int = 20,
) -> str:
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model.to(device)

    newline_id = tokenizer.encode("\n", add_special_tokens=False)[0]
    tokenizer.pad_token = "\n"
    tokenizer.eos_token = "\n"

    inputs = tokenizer(prompt, return_tensors="pt", padding=True, truncation=True)
    inputs = {key: value.to(device) for key, value in inputs.items()}

    outputs = model.generate(
        inputs["input_ids"],
        attention_mask=inputs["attention_mask"],
        max_new_tokens=max_length,
        num_return_sequences=1,
        do_sample=False,
        temperature=0.7,
        pad_token_id=newline_id,
        eos_token_id=newline_id,
    )
    full_generated = tokenizer.decode(outputs[0], skip_special_tokens=True).strip()

    # take first new line after prompt, or full output if no \n
    generated_after_prompt = full_generated[len(prompt) :].strip()
    return (
        generated_after_prompt.split("\n")[0].strip() if generated_after_prompt else ""
    )


def generate_completion_outputs(
    inputs_path: str,
    output_path: str,
    model,
    tokenizer,
    separator="__###__",
    subset_size=None,
):
    if not os.path.exists(inputs_path):
        raise FileNotFoundError(f"File not found: {inputs_path}")

    results = []
    with open(inputs_path, "r", encoding="utf-8") as f:
        eval_lines = f.readlines()
    if subset_size:
        eval_lines = random.sample(eval_lines, min(subset_size, len(eval_lines)))

    for line in tqdm(eval_lines, desc="Generating outputs", total=len(eval_lines)):
        try:
            entry = json.loads(line.strip())
            if "text" not in entry:
                continue
            text = entry["text"]
            if separator not in text:
                continue
            input_text, target = text.split(separator)
            input_text = input_text.strip()
            target = target.strip()

            output = run_model(model, tokenizer, input_text)
            results.append({"input": input_text, "output": output, "target": target})

        except (json.JSONDecodeError, ValueError):
            print(f"Error processing line: {line.strip()}")
            continue

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)
    print(f"Eval results saved to {output_path}")
    return results


if __name__ == "__main__":
    input_path = os.path.join(current_path, "..", "data", "evaluation", "snippets")
    model = "starcoder_3b_local"
    model_path = os.path.join(current_path, "..", "models", model)
    output_path = os.path.join(
        current_path, "..", "data", "evaluation", "finetuned_predictions.json"
    )
    model, tokenizer = load_model(model_path)
    generate_completion_outputs(input_path, output_path, model, tokenizer)
