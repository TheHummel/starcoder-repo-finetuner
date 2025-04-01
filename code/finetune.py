import os
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer, TrainingArguments, Trainer
from datasets import load_dataset
from peft import LoraConfig, get_peft_model
import psutil

current_path = os.path.dirname(os.path.abspath(__file__))


def finetune(model_path: str):
    print(f"Memory before loading: {psutil.virtual_memory().percent}% used")

    # load model and tokenizer
    if not os.path.exists(model_path):
        raise FileNotFoundError(f"File not found: {model_path}")

    tokenizer = AutoTokenizer.from_pretrained(model_path, padding_side="left")
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token

    model = AutoModelForCausalLM.from_pretrained(
        model_path,
        torch_dtype=torch.bfloat16,
        device_map="cpu",
    )
    print(f"Model loaded! Memory: {psutil.virtual_memory().percent}% used")

    # load dataset
    dataset = load_dataset(
        "json", data_files="../data/training/train.jsonl", split="train"
    )
    print(f"Dataset loaded: {len(dataset)} examples")
    dataset = dataset.select(range(min(500, len(dataset))))

    # tokenize dataset
    def tokenize_function(examples):
        return tokenizer(
            examples["text"], padding=True, truncation=True, max_length=256
        )

    tokenized_dataset = dataset.map(
        tokenize_function, batched=True, remove_columns=["text"]
    )
    tokenized_dataset = tokenized_dataset.map(
        lambda x: {**x, "labels": x["input_ids"].copy()}
    )
    print(f"Dataset tokenized! Memory: {psutil.virtual_memory().percent}% used")

    # LORA
    lora_config = LoraConfig(
        r=16,
        lora_alpha=32,
        target_modules=["c_attn"],
        lora_dropout=0.05,
        bias="none",
        task_type="CAUSAL_LM",
    )
    model = get_peft_model(model, lora_config)
    model.print_trainable_parameters()
    print(f"LoRA applied! Memory: {psutil.virtual_memory().percent}% used")

    # training
    training_args = TrainingArguments(
        output_dir="../data/finetuned_model",
        per_device_train_batch_size=2,
        gradient_accumulation_steps=2,
        num_train_epochs=2,
        learning_rate=2e-4,
        save_steps=500,
        logging_steps=10,
    )

    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=tokenized_dataset,
    )

    try:
        trainer.train()
    except Exception as e:
        print(f"Training crashed: {str(e)}")
        raise

    # save
    output_dir = os.path.join(current_path, "..", "models", "finetuned_model")
    os.makedirs(output_dir, exist_ok=True)
    model.save_pretrained(output_dir)
    tokenizer.save_pretrained(output_dir)

    print("Finetuning complete!")


if __name__ == "__main__":
    model_path = os.path.join(current_path, "..", "models", "starcoder_3b_local")
    finetune(model_path)
