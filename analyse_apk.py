import sys
import glob
import json
from enum import Enum

import analyser.analyse_apk
import analyser.analyse_apk_paralel
import analyser.evaluate_analyser
import analyser.evaluate_perm_mapping
import scraping.multi_thread

class Help(Enum):
    ANALYSE = ""
    ANALYSE_PAR = """
Analyses each APK file with each of the 9 models trained in the main.ipynb file.
Each model launches in its own thread
The APK files to analyse are listed in the `dataset/apk/apk_info.csv` file, which serves as a filter over the full dataset.
The data of each APK file is in the `dataset/apk/app_info_FINAL.json` file, which is a cache of each APK's permissions and categories. This avoids the analysis of the APK files and scraping the web for categories, making the analysis faster and more reliable.
This file can be obtained by running `python analyse_apk.py scrape` and `python analyse_apk.py merge_app`, which will inspect the APKs and scrape the permissions and then merge all information into a single file.
The results of execution are stored in `out/apk_analysis_<dist_func>.json`, where `dist_func` is the distance function used to map permissions and categories from the APK into the features of the model.
The results are a map of the APK package to an object mapping each model to its analysis of the APK.
    """
    MAP_APKS = """
Fetches the features the models' mapping function extracts from the APKs.
The input are not the APKs themselves, but the data in `dataset/apk/apk_info.csv`.
This file can be obtained by running `python analyse_apk.py scrape` and `python analyse_apk.py merge_app`, which will inspect the APKs and scrape the permissions and then merge all information into a single file.
The results of execution are stored in `out/apk_analysis_<dist_func>.json`, where `dist_func` is the distance function used to map permissions and categories from the APK into the features of the model.
The results are a map of the APK package to the features the model would map it into, as well as those in the actual dataset the model was trained on.
    """
    SCRAPE = """
Given a list of APKs, fetch their categories from apkpure.com, if available.
Note that application categories change over time and applications get removed from the internet, meaning scraping is not always reliable.
The scraping is multi threaded and can use proxies to evade bot detection.
The proxy list argument is a URL from which a plain text file with one HTTP proxy URL per line can be directly downloaded.
Scraping can be stoped at any time by pressing Ctrl+C, and then resumed at a later time. Note that all threads must finish their work and the file must be writen before the scraper is actually closed, which can take 1 minute.
The resulting data is stored in `data/app_cats_XXX.json` files, one per scraping session.
    """
    EVAL_ANALYSER = """
Reads datasets and analysis results in `out/apk_analysis_*.json` to determine how often the models agree with each other on whether an APK is malicious.
The graph is stored in `out/analysis_model_consensus_plot.png`, showing how often x% of the models agree on the evaluation.
    """
    EVAL_MAPPING = """
Create box plots of the correctness of the predictions of classes given to each APK.
A class can be a permission or a category.
The program generates 3 images, one for categories alone, other for permissions and another with both.
Each image will have 3 figures, one that shows how many guesses were in the original dataset, another showing how many elements from the dataset were in the guesses and another showing how many were in both.
These images are stored in `/tmp/<fn>/categories_box_plots.png`, where `fn` is the mapping function used.
"""
    MERGE_APP = """ 
Merges all `dataset/apk/app_info_*.json` files into `dataset/apk/app_info_FINAL.json`.
"""
    PERM_LIST = """
Obtains the set of permissions from all APKs in `dataset/apk/app_info_FINAL.json` and writes it to `dataset/permissions.json`.
"""


def print_better_help(key: str):
    print(Help[key.upper()].value)

def print_help():
    print("""
analyse_apk: analyse one or more apk files and test the analysis process.

Arguments:

help <command>: display further information about a specific command

analyse_par [apks]: run multithreaded analysis on the apks, or on those in dataset/apks if no apk is specified

map_apks [apks]: Fetch the permissions and categories of each APK file, but do not analyse it

scrape <proxy_url> <num_threads>: scrape the categories of a list of APK files, given a proxy list and number of threads for the scraping

eval_analyser: create a bar plot of the consensus rate of the analysers, based on the last analysis

eval_mapping: create box plots showing the percentage of correct and incorrect guesses by a permission mapping function

merge_app: merge all app information obtained through the various scraping sessions. Creates `dataset/apk/app_info_FINAL.json`

perm_list: generate the set of all permissions from the `dataset/apk/app_info_FINAL.json` file
    """)

def merge_app_info():
    apps = {}
    for fname in glob.glob("dataset/apk/app_info_*.json"):
        with open(fname) as f:
            data = json.loads(f.read())
            apps |= data

    with open("dataset/apk/app_info_FINAL.json", 'w') as f:
        f.write(json.dumps(apps))

def generate_permission_list():
    with open("dataset/apk/app_info_FINAL.json") as f:
        info = json.loads(f.read())
    
    perms = set()
    for app in info:
        perms |= set(info[app]["permissions"])

    with open("dataset/permissions.json", 'w') as f:
        f.write(json.dumps(list(perms))) 

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print_help()
        sys.exit(1)

    if len(sys.argv) == 2:
        prog, args = sys.argv[1], []
    else:
        prog, args = sys.argv[1], sys.argv[2:]
    
    if prog == "scrape":
        # in:   dataset/apk/to_analyse.json (create ine)
        #       dataset/apk/apk_info.csv (create ine)
        # out:  dataset/apk/app_info_XXX.json
        #       dataset/apk/apk_info.csv
        if len(args) < 2:
            print_help()
            sys.exit(1)
        proxy_url = args[0]
        num_threads = int(args[1])
        scraping.multi_thread.scrape_local_apks(num_threads, proxy_url)
        
        # TODO: merge all files into one, dataset/apk/app_info_FINAL.json
    # elif prog == "analyse":
    #     analyser.analyse_apk.main(args)
    elif prog == "analyse_par":
        # in:   dataset/apk/app_info_FINAL.json        ---------------------
        #       dataset/apk/apk_info.csv
        # out:  out/apk_analysis_{apk.model.dist_func.__name__}.json

        analyser.analyse_apk_paralel.GET_FEATURES = False
        analyser.analyse_apk_paralel.main(args)    
    elif prog == "map_apks":
        # in:   dataset/apk/app_info_FINAL.json        ---------------------
        #       dataset/apk/apk_info.csv
        # out:  out/apk_analysis_{apk.model.dist_func.__name__}.json

        analyser.analyse_apk_paralel.GET_FEATURES = True
        analyser.analyse_apk_paralel.main(args)    
    elif prog == "eval_analyser":
        # in:   out/apk_analysis.json
        #       dataset/abig_heuristic.csv             ---------------------
        #       dataset/exodus_heuristic.csv           ---------------------
        # out:  out/analysis_model_consensus_plot.png

        analyser.evaluate_analyser.main()
    elif prog == "eval_mapping":
        # in:   out/apk_analysis_{apk.model.dist_func.__name__}.json
        #       dataset/permissions.json                --------------------
        # out:  dataset/perm_map_{fn_name}.json
        #       /tmp/{fn}/XXX_box_plots.png

        analyser.evaluate_perm_mapping.main()
    elif prog == "merge_app":
        merge_app_info()
    elif prog == "perm_list":
        generate_permission_list()
    elif prog == "help":
        pass
    else: 
        print_help()