import json

import matplotlib.pyplot as plt
from collections import Counter


def plot_occurrences(float_list):
    counts = Counter(float_list)
    
    floats = list(counts.keys())
    counts = list(counts.values())
    
    plt.figure(figsize=(8, 6))
    bars = plt.bar(floats, counts, width=0.1, color='skyblue', edgecolor='black')
    
    i = 0
    for bar in bars:
        plt.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.1, 
                 f'{counts[i]}', ha='center', va='bottom', fontsize=10)
        i += 1

    plt.xlabel('Consensus')
    plt.ylabel('Occurrences')
    plt.title('Model consensus rate')
    plt.xticks(rotation=45)
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    
    plt.savefig('out/analysis_model_consensus_plot.png')



print("Reading analysed apps...")
with open("out/apk_analysis.json") as f:
    analysed = json.loads(f.read())
    analysed = {
        k: { 
            k1: analysed[k][k1] == 'True'
            for k1 in analysed[k]
        }
        for k in analysed
    }

model_consensus = []

for app in analysed:
    anomally = len([model for model in analysed[app] if 'apd' not in model and analysed[app][model]])
    norm = max(anomally, 6-anomally)
    model_consensus.append(norm/6)

plot_occurrences(model_consensus)

print("Reading abig dataset...")
with open("dataset/abig_heuristic.csv") as f:
    abig_heuristic = [ln.split() for ln in f.readlines()][1:]
    abig_heuristic = {k: v == '1' for k, v in abig_heuristic}

print("Reading exodus dataset...")
with open("dataset/exodus_heuristic.csv") as f:
    exodus_heuristic = [ln.split() for ln in f.readlines()][1:]
    exodus_heuristic = {k: v == '1' for k, v in exodus_heuristic}

DATASETS = {
    'exodus': exodus_heuristic,
    'abig': abig_heuristic,
}

MODELS = (
    'ae',
    'vae',
    'sae',
)

print(len([a for a in analysed if a in abig_heuristic])/len(analysed))
print(len([a for a in analysed if a in exodus_heuristic])/len(analysed))

for ds_name in DATASETS:
    ds = DATASETS[ds_name]

    for model in MODELS:
        results = [
            ds[k] == analysed[k][f"{ds_name}_{model}"]
            for k in analysed
            if k in ds
        ]

        correct_percent = len([r for r in results if r])/len(results)
        print(f"Dataset '{ds_name}', Model '{model}', Accuracy {correct_percent*100}% ({len(results)} apps)")
