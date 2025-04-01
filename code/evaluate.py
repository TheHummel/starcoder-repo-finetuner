import json
from nltk.translate.bleu_score import sentence_bleu, SmoothingFunction
import os

current_path = os.path.dirname(os.path.abspath(__file__))


def load_json(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)


def compute_metrics(prediction, target):
    # exact match
    exact_match = prediction == target

    target = [target.split()]
    prediction = prediction.split()

    bleu = sentence_bleu(
        target,
        prediction,
        weights=(0.5, 0.5, 0, 0),
        smoothing_function=SmoothingFunction().method1,
    )

    return exact_match, bleu


def evaluate_predictions(baseline_data, finetuned_data):
    if len(baseline_data) != len(finetuned_data):
        raise ValueError(
            "Baseline and finetuned JSONs don't have the same number of entries"
        )

    results = []
    baseline_exact_matches = 0
    baseline_bleu_sum = 0
    finetuned_exact_matches = 0
    finetuned_bleu_sum = 0
    total = len(baseline_data)

    for baseline, finetuned in zip(baseline_data, finetuned_data):
        if (
            baseline["input"] != finetuned["input"]
            or baseline["target"] != finetuned["target"]
        ):
            raise ValueError(
                "Mismatched prompts or targets between baseline and finetuned"
            )

        baseline_exact, baseline_bleu = compute_metrics(
            baseline["output"], baseline["target"]
        )
        finetuned_exact, finetuned_bleu = compute_metrics(
            finetuned["output"], finetuned["target"]
        )

        baseline_exact_matches += int(baseline_exact)
        baseline_bleu_sum += baseline_bleu
        finetuned_exact_matches += int(finetuned_exact)
        finetuned_bleu_sum += finetuned_bleu

        result = {
            "input": baseline["input"],
            "target": baseline["target"],
            "baseline_prediction": baseline["output"],
            "baseline_exact_match": baseline_exact,
            "baseline_bleu_score": baseline_bleu,
            "finetuned_prediction": finetuned["output"],
            "finetuned_exact_match": finetuned_exact,
            "finetuned_bleu_score": finetuned_bleu,
        }
        results.append(result)

    # summary stats
    baseline_accuracy = baseline_exact_matches / total
    baseline_avg_bleu = baseline_bleu_sum / total
    finetuned_accuracy = finetuned_exact_matches / total
    finetuned_avg_bleu = finetuned_bleu_sum / total

    print(
        f"Baseline Exact Match Accuracy: {baseline_accuracy:.2%} ({baseline_exact_matches}/{total})"
    )
    print(f"Baseline Average BLEU Score: {baseline_avg_bleu:.4f}")
    print(
        f"Finetuned Exact Match Accuracy: {finetuned_accuracy:.2%} ({finetuned_exact_matches}/{total})"
    )
    print(f"Finetuned Average BLEU Score: {finetuned_avg_bleu:.4f}")

    return results


if __name__ == "__main__":
    baseline_json = os.path.join(
        current_path, "..", "data", "evaluation", "baseline_predictions.json"
    )
    finetuned_json = os.path.join(
        current_path, "..", "data", "evaluation", "finetuned_predictions.json"
    )
    output_file = os.path.join(
        current_path, "..", "data", "evaluation", "comparison.jsonl"
    )

    baseline_data = load_json(baseline_json)
    finetuned_data = load_json(finetuned_json)

    results = evaluate_predictions(baseline_data, finetuned_data)

    # save results
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    with open(output_file, "w", encoding="utf-8") as f:
        for result in results:
            f.write(json.dumps(result) + "\n")

    print(f"Comparison saved to {output_file}")
