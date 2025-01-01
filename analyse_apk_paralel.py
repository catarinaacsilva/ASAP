import sys
import os
import csv
import json
import concurrent.futures
from queue import Queue
# import tensorflow as tf
import numpy as np
from tqdm.keras import TqdmCallback

from scraping.apk_info import extract_apk_info
# from apk.model import ABigModel, APDModel, ExodusModel
import apk.model

from eval_mapping import get_one_hot_columns


GET_FEATURES = True

with open("dataset/apk/app_info_FINAL.json") as f:
    apk_data = json.loads(f.read())

def process_apk_with_model(model, apk_paths, result_queue):
    """
    Process each APK for a specific model.
    """
    for apk_path in apk_paths:
        try:
            info = apk_data[apk_path] # extract_apk_info(apk_path, scrape_categories=False)
            app_pkg = info['app_id']
            perms = info['permissions']
            cats = info['categories']
            
            # Process the APK with the model
            print(f"Processing {apk_path} with model {model.name}")

            if GET_FEATURES:
                res = model.get_apk_features(perms, cats)
            else:
                res = model.analyse_apk(perms, cats)

            result_queue.put((app_pkg, model.name, res))
        except Exception as e:
            print(f"ERROR processing {apk_path} with model {model.name}: {e}")
            result_queue.put((app_pkg, model.name, f"Error: {str(e)}"))


def save_results(results, output_file):
    print("Saving results, do not quit!")
    data = {}
    for apk, model, res in results:
        if apk not in data:
            data[apk] = {}
        if GET_FEATURES:
            data[apk][model] = list(set(res))
        else:
            data[apk][model] = str(res)
    
    if GET_FEATURES:
        for apk in data:
            try:
                data[apk]["abig"] = list(set(get_one_hot_columns(apk)))
            except ValueError:
                continue

    with open(output_file, 'w') as f:
        f.write(json.dumps(data))

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

def main():
    if len(sys.argv) < 2:
        # print(f"usage: python {sys.argv[0]} <path to apk1> <path to apk2> ... <path to apkN>")
        # sys.exit(1)
        with open("dataset/apk/apk_info.csv") as f:
            apk_paths = [ln[:-1] for ln in f.readlines()]
    else:
        apk_paths = sys.argv[1:]

    # store = apk.model.WordImportanceStorage(PERMISSIONS)
    # apk.model.dist_func = store.token_inclusion_distance_with_word_importance

    if GET_FEATURES:
        models = [
            apk.model.ABigModel("out/abig_sae.keras"),
        ]
    else:
        models = [
            apk.model.APDModel("out/apd_ae.keras"),
            apk.model.ExodusModel("out/exodus_ae.keras"),
            apk.model.ABigModel("out/abig_ae.keras"),
            apk.model.APDModel("out/apd_vae.keras"),
            apk.model.ExodusModel("out/exodus_vae.keras"),
            apk.model.ABigModel("out/abig_vae.keras"),
            apk.model.APDModel("out/apd_sae.keras"),
            apk.model.ABigModel("out/abig_sae.keras"),
            apk.model.ExodusModel("out/exodus_sae.keras"),
        ]

    result_queue = Queue()

    # One thread per model
    with concurrent.futures.ThreadPoolExecutor(max_workers=len(models)) as executor:
        futures = []
        for model in models:
            futures.append(executor.submit(process_apk_with_model, model, apk_paths, result_queue))
        
        for future in futures:
            future.result()

        results = []
        while not result_queue.empty():
            results.append(result_queue.get())
        
        res_path = f"out/apk_analysis_{apk.model.dist_func.__name__}.json"
        save_results(results, res_path)
        print(f"Results saved to '{res_path}'")


if __name__ == "__main__":
    main()
