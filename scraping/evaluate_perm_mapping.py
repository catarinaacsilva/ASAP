PERMISSIONS = [s.lower() for s in [
            "set preferred apps",
            "read terms you added to the dictionary",
            "reroute outgoing calls",
            "expand/collapse status bar",
            "modify global animation speed",
            "force background apps to close",
            "add voicemail",
            "read your text messages (SMS or MMS)",
            "directly call any phone numbers",
            "read battery statistics",
            "act as the AccountManagerService",
            "limit number of running processes",
            "receive text messages (WAP)",
            "set time zone",
            "write web bookmarks and history",
            "Change WiMAX state",
            "change/intercept network settings and traffic",
            "body sensors (like heart rate monitors)",
            "send Linux signals to apps",
            "write call log",
            "read cell broadcast messages",
            "receive text messages (MMS)",
            "enable app debugging",
            "access serial ports",
            "erase USB storage",
            "receive text messages (SMS)",
            "modify your own contact card",
            "modify phone state",
            "make/receive SIP calls",
            "add words to user-defined dictionary",
            "edit your text messages (SMS or MMS)",
            "make app always run",
            "retrieve system internal state",
            "read call log",
            "send SMS messages",
            "measure app storage space",
        ]]
CATEGORIES = [
           "detective",
           "super hero",
           "girls",
           "multiple characters",
           "norse mythology",
           "__error__",
           "draughts",
           "p v e",
           "bl",
           "player",
           "multimedia",
           "drums",
           "shopping",
           "livestreaming video games",
           "location-based",
           "nail salon",
           "crafting",
           "hearing assistance",
           "calling",
           "superstar smtown",
           "sony",
           "video sharing",
           "office",
           "learning",
           "stg",
           "sports",
           "renovate & decorat",
           "cv",
           "teen patti",
           "social media",
           "health",
           "lifestyle",
           "acg",
           "customization",
           "uta no☆prince-sama",
           "adv",
           "games",
        ]

import json
import matplotlib.pyplot as plt
import polars as pl
from collections import defaultdict
from pathlib import Path
import apk.model

EXP = "abig_sae"
REF = "abig"

def calculate_percentages(experiment, reference):
    # Convert lists to sets for easy comparison
    experiment_set = set(experiment)
    reference_set = set(reference)

    # Calculate intersection and differences
    intersection = experiment_set & reference_set
    only_in_experiment = experiment_set - reference_set
    only_in_reference = reference_set - experiment_set

    # Calculate percentages
    total_experiment = len(experiment_set)
    total_reference = len(reference_set)
    
    percent_in_both = (len(intersection) / min(total_experiment, total_reference)) * 100 if total_experiment and total_reference else 0
    percent_in_experiment_only = (len(only_in_experiment) / total_experiment) * 100 if total_experiment else 0
    percent_in_reference_only = (len(only_in_reference) / total_reference) * 100 if total_reference else 0
    
    return percent_in_both, percent_in_experiment_only, percent_in_reference_only

def calculate_difference(experiment, reference):
    # Calculate the absolute difference between the percentages of the two lists
    percent_in_both, percent_in_experiment_only, percent_in_reference_only = calculate_percentages(experiment, reference)
    total_percent_diff = abs(percent_in_both - percent_in_experiment_only - percent_in_reference_only)
    return total_percent_diff, percent_in_both, percent_in_experiment_only, percent_in_reference_only

def analyze_json(file_path, fn):
    with open(file_path, 'r') as file:
        data = json.load(file)
        data.pop("__NONE__", None)
    
    # Prepare data for analysis
    results = defaultdict(list)
    
    permissions_data = defaultdict(list)
    categories_data = defaultdict(list)
    
    discrepancies = []
    permissions_discrepancies = []
    categories_discrepancies = []
    
    for data_point, experiments in data.items():
        experiment = experiments.get(EXP, [])
        reference = experiments.get(REF, [])
        
        # Calculate the difference for the full list
        total_diff, percent_in_both, percent_in_experiment_only, percent_in_reference_only = calculate_difference(experiment, reference)
        
        # Handle the PERMISSIONS and CATEGORIES separately
        permission_experiment = [item for item in experiment if item in PERMISSIONS]
        permission_reference = [item for item in reference if item in PERMISSIONS]
        category_experiment = [item for item in experiment if item in CATEGORIES]
        category_reference = [item for item in reference if item in CATEGORIES]
        
        perm_diff, perm_in_both, perm_in_experiment_only, perm_in_reference_only = calculate_difference(permission_experiment, permission_reference)
        cat_diff, cat_in_both, cat_in_experiment_only, cat_in_reference_only = calculate_difference(category_experiment, category_reference)
        
        # Store results for each data point
        results["Data Point"].append(data_point)
        results["Percent in Both"].append(percent_in_both)
        results["Percent in Mapping Only"].append(percent_in_experiment_only)
        results["Percent in Dataset Only"].append(percent_in_reference_only)
        
        permissions_data["Percent in Both"].append(perm_in_both)
        permissions_data["Percent in Mapping Only"].append(perm_in_experiment_only)
        permissions_data["Percent in Dataset Only"].append(perm_in_reference_only)
        
        categories_data["Percent in Both"].append(cat_in_both)
        categories_data["Percent in Mapping Only"].append(cat_in_experiment_only)
        categories_data["Percent in Dataset Only"].append(cat_in_reference_only)
        
        # Track discrepancies
        discrepancies.append((data_point, total_diff))
        permissions_discrepancies.append((data_point, perm_diff))
        categories_discrepancies.append((data_point, cat_diff))

    Path(f"/tmp/{fn}").mkdir(parents=True, exist_ok=True)

    # Sort discrepancies by the largest difference
    discrepancies.sort(key=lambda x: x[1], reverse=True)
    permissions_discrepancies.sort(key=lambda x: x[1], reverse=True)
    categories_discrepancies.sort(key=lambda x: x[1], reverse=True)

    # Print out the data points with the biggest discrepancies
    print("Top 5 data points with the largest total discrepancies (combined):")
    for data_point, diff in discrepancies[:5]:
        print(f"{data_point}: {diff:.2f}% difference")

    print("\nTop 5 data points with the largest discrepancies in PERMISSIONS:")
    for data_point, diff in permissions_discrepancies[:5]:
        print(f"{data_point}: {diff:.2f}% difference")

    print("\nTop 5 data points with the largest discrepancies in CATEGORIES:")
    for data_point, diff in categories_discrepancies[:5]:
        print(f"{data_point}: {diff:.2f}% difference")

    # Convert results to a Polars DataFrame
    df = pl.DataFrame(results)
    perm_df = pl.DataFrame(permissions_data)
    cat_df = pl.DataFrame(categories_data)
    
    # Extract the columns as lists to plot using Matplotlib
    percent_in_both = df["Percent in Both"].to_list()
    percent_in_experiment_only = df["Percent in Mapping Only"].to_list()
    percent_in_reference_only = df["Percent in Dataset Only"].to_list()
    
    perm_in_both = perm_df["Percent in Both"].to_list()
    perm_in_experiment_only = perm_df["Percent in Mapping Only"].to_list()
    perm_in_reference_only = perm_df["Percent in Dataset Only"].to_list()
    
    cat_in_both = cat_df["Percent in Both"].to_list()
    cat_in_experiment_only = cat_df["Percent in Mapping Only"].to_list()
    cat_in_reference_only = cat_df["Percent in Dataset Only"].to_list()
    
    # Create box plots for the combined data
    fig, axes = plt.subplots(1, 3, figsize=(18, 6))
    
    # Boxplot for Percent in Both
    axes[0].boxplot(percent_in_both)
    axes[0].set_title("Percentage in Both (Combined)")
    
    # Boxplot for Percent in Experiment Only
    axes[1].boxplot(percent_in_experiment_only)
    axes[1].set_title("Percentage in Mapping Only (Combined)")
    
    # Boxplot for Percent in Reference Only
    axes[2].boxplot(percent_in_reference_only)
    axes[2].set_title("Percentage in Dataset Only (Combined)")
    
    plt.tight_layout()
    plt.savefig(f'/tmp/{fn}/combined_box_plots.png', bbox_inches='tight')
    plt.close()

    # Create box plots for PERMISSIONS data
    fig, axes = plt.subplots(1, 3, figsize=(18, 6))
    
    # Boxplot for Percent in Both (Permissions)
    axes[0].boxplot(perm_in_both)
    axes[0].set_title("Percentage in Both (Permissions)")
    
    # Boxplot for Percent in Experiment Only (Permissions)
    axes[1].boxplot(perm_in_experiment_only)
    axes[1].set_title("Percentage in Mapping Only (Permissions)")
    
    # Boxplot for Percent in Reference Only (Permissions)
    axes[2].boxplot(perm_in_reference_only)
    axes[2].set_title("Percentage in Dataset Only (Permissions)")
    
    plt.tight_layout()
    plt.savefig(f'/tmp/{fn}/permissions_box_plots.png', bbox_inches='tight')
    plt.close()

    # Create box plots for CATEGORIES data
    fig, axes = plt.subplots(1, 3, figsize=(18, 6))
    
    # Boxplot for Percent in Both (Categories)
    axes[0].boxplot(cat_in_both)
    axes[0].set_title("Percentage in Both (Categories)")
    
    # Boxplot for Percent in Experiment Only (Categories)
    axes[1].boxplot(cat_in_experiment_only)
    axes[1].set_title("Percentage in Mapping Only (Categories)")
    
    # Boxplot for Percent in Reference Only (Categories)
    axes[2].boxplot(cat_in_reference_only)
    axes[2].set_title("Percentage in Dataset Only (Categories)")
    
    plt.tight_layout()
    plt.savefig(f'/tmp/{fn}/categories_box_plots.png', bbox_inches='tight')
    plt.close()

# Example usage
if __name__ == "__main__":
    functions = (
        # apk.model.simple_token_inclusion_distance,
        # apk.model.jaccard_similarity,
        apk.model.semantic_distance,
    )

    for fn in functions:
        apk.model.dist_func = fn
        fn_name = fn.__name__

        file_path = f'out/apk_analysis_{fn_name}.json'

        analyze_json(file_path, fn_name)

        with open("dataset/permissions.json") as f:
            all_perms = json.loads(f.read())
        
        # store = apk.model.WordImportanceStorage(PERMISSIONS)
        # apk.model.dist_func = store.token_inclusion_distance_with_word_importance

        model = apk.model.ABigModel("out/abig_sae.keras")

        perm_map = {p: [] for p in [*PERMISSIONS, "__NONE__"]}
        for perm in all_perms:
            mapped = model.map_permission(perm)
            
            if mapped is not None:
                perm_map[mapped].append(perm)
            else:
                perm_map["__NONE__"].append(perm)

        with open(f"dataset/perm_map_{fn_name}.json", 'w') as f:
            f.write(json.dumps(perm_map))