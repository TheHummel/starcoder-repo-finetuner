import os
from tqdm import tqdm

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
from dotenv import load_dotenv

from nltk.translate.bleu_score import sentence_bleu

load_dotenv()
hf_token = os.getenv("HF_TOKEN")
if not hf_token:
    raise ValueError("HF_TOKEN not found.")

current_path = os.path.dirname(os.path.abspath(__file__))
model_path = os.path.join(current_path, "../models/starcoder_3b_local")
tokenizer = AutoTokenizer.from_pretrained(model_path, padding_side="left")
tokenizer.pad_token = tokenizer.eos_token
model = AutoModelForCausalLM.from_pretrained(
    model_path, torch_dtype=torch.float16, device_map="cpu"
)
print("Model loaded!")


def generate_code(prompt, max_length=100):
    inputs = tokenizer(prompt, return_tensors="pt", padding=True, truncation=True)
    outputs = model.generate(
        inputs["input_ids"],
        attention_mask=inputs["attention_mask"],
        max_length=max_length,
        num_return_sequences=1,
        do_sample=True,
        temperature=0.7,
        pad_token_id=tokenizer.eos_token_id,
    )
    return tokenizer.decode(outputs[0], skip_special_tokens=True).strip()


completion_tests = [
    (
        "import scrapy\nclass MySpider(scrapy.Spider):\n    name = 'myspider'\n    start_urls = ['http://example.com']\n    def parse(self, response):\n        ",
        "yield {'title': response.css('title::text').get()}",
    ),
    (
        "import scrapy\nclass BlogSpider(scrapy.Spider):\n    name = 'blog'\n    start_urls = ['http://blog.com']\n    def parse(self, response):\n        ",
        "for post in response.css('div.post'):\n            yield {'title': post.css('h1::text').get()}",
    ),
]
completion_truth = [prefix + truth for prefix, truth in completion_tests]

generation_tests = [
    "Given 'class NewsSpider(scrapy.Spider):', scrape headlines",
    "Given 'import scrapy', define a spider for products",
]
generation_truth = [
    "class NewsSpider(scrapy.Spider):\n    name = 'news'\n    start_urls = ['http://news.com']\n    def parse(self, response):\n        yield {'headline': response.css('h1::text').get()}",
    "import scrapy\nclass ProductSpider(scrapy.Spider):\n    name = 'products'\n    start_urls = ['http://store.com']\n    def parse(self, response):\n        yield {'name': response.css('.product::text').get()}",
]

print("\n=== Code Completion Baseline ===")
for prefix, truth in tqdm(
    zip(completion_tests, completion_truth), total=len(completion_tests)
):
    generated = generate_code(prefix)
    bleu = sentence_bleu([truth.split()], generated.split())
    exact = generated.strip() == truth.strip()
    print(f"Prefix:\n{prefix}")
    print(f"Generated:\n{generated}")
    print(f"Truth:\n{truth}")
    print(f"BLEU: {bleu:.3f}, Exact: {exact}\n")

print("\n=== Code Generation Baseline ===")
for prompt, truth in tqdm(
    zip(generation_tests, generation_truth), total=len(generation_tests)
):
    generated = generate_code(prompt)
    bleu = sentence_bleu([truth.split()], generated.split())
    exact = generated.strip() == truth.strip()
    print(f"Prompt: {prompt}")
    print(f"Generated:\n{generated}")
    print(f"Truth: {truth}")
    print(f"BLEU: {bleu:.3f}, Exact: {exact}\n")
