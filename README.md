# StarCoder Finetuning for Repository-Specific Code Completion

This project uses the [StarCoderBase-3B](https://huggingface.co/bigcode/starcoderbase-3b) model to finetune its completion capabilities to a specific codebase. The purpose is to enhance StarCoder’s ability to predict accurate, context-aware code for any repository, leveraging lightweight finetuning techniques like LoRA.

## Overview

The StarCoder model is finetuned using LoRA (Low-Rank Adaptation) to adapt its parameters to a target repository. The process involves:

- **Load Model:** Start with the pretrained StarCoder model.
- **Snippet Extraction:** Parse source files into manageable code chunks for training.
  - **Training Set:** Extract snippets from the target repository, focusing on relevant code sections (e.g., functions, classes).
  - **Evaluation Set:** Create a separate set of snippets for model evaluation.
- **Dataset Prep:** Convert snippets into a `.jsonl` file for training.
- **Finetuning:** Apply LoRA (`r=8`, `dropout=0.25`, `lr=3e-5`) on the training set.
- **Generate outputs:** Generate code completions for a separate evaluation set for both baseline and finetuned models.
- **Evaluation:** Measure exact match and BLEU scores on created outputs, comparing baseline vs. finetuned outputs.

## Contents

- **`code/`**
  - **`evaluate.py`:** Computes exact match and BLEU scores for model predictions and compares baseline and finetuned models' predictions.
  - **`finetune.py`:** Core script for LoRA-based finetuning of StarCoder.
  - **`generate_training_set.py`:** Extracts code snippets from a repository for training/finetuning.
  - **`generate_evaluation_set.py`:** Extracts code snippets from a repository to run the evaluation on.
  - **`run_inference.py`:** Runs inference on the finetuned model to generate predictions.
  - **`colab/`**
    - **`finetune_and_eval.ipynb`:** Notebook for finetuning the model using Google Colab.

## Example: Klicker-UZH Finetuning

As a demonstration, I finetuned StarCoderBase-3B on TypeScript code from [Klicker-UZH](https://github.com/uzh-bf/klicker-uzh), an open-source audience interaction platform from University of Zurich:

- **Training Data:** Extracted functions in snippets from `apps/` TS files filtering out files containing the practice quizzes logic which were used for evaluation.
- **Evaluation Data:** For each TS function from the files containing the practice quizzes logic, created snippet for each line (prefix = imports + prior lines inside respective fuction, target = next line), simulating partial code completion within the repo.
- **Finetuning:** Ran on Colab (T4 GPU) with LoRA, hitting 43.13% exact match (BLEU 0.2581) from 40.82% (BLEU 0.2470) baseline.
- **Evaluation:** Tested on 1,776 snippets from practice quiz TS files, mimicking a scenario where quiz logic is implemented given the rest of the repo.

### Data and Models

[Google Drive](https://drive.google.com/drive/folders/1phqbtTi_HL8fwEw576SmxQqqi-XYDouL?usp=drive_link)

- `train.jsonl`: Training snippets
- `evaluation.jsonl`: Evaluation snippets
- `finetuned_model_final/`: Finetuned model weights
- `baseline_predicitons.json`, `finetuned_predicitons.json`: Prediction results

### Results

- **Baseline:** 40.82% exact (725/1,776), BLEU 0.2470
- **Finetuned:** 43.13% exact (766/1,776), BLEU 0.2581
