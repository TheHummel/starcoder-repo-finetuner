import os
import json


def convert_dataset_to_jsonl(input_dir: str, output_file: str, separator: str = "\n"):

    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    with open(output_file, "w", encoding="utf-8") as f_out:
        for filename in os.listdir(input_dir):
            if filename.endswith(".txt"):
                with open(
                    os.path.join(input_dir, filename), "r", encoding="utf-8"
                ) as f_in:
                    text = f_in.read()
                    prompt, completion = text.split("__OUTPUT__: ")
                    prompt = prompt.replace("__INPUT__: ", "").strip()
                    completion = completion.strip()
                    # combine prompt and completion with a separator
                    f_out.write(
                        json.dumps({"text": f"{prompt}{separator}{completion}"}) + "\n"
                    )

    print(f"Dataset prepared at {output_file}")
