"""
Analyses a single APK file with the models from main.ipynb
"""

import sys
import gzip
import tensorflow as tf
import numpy as np
import polars as pl
import tensorflow.keras.backend as K
from tqdm.keras import TqdmCallback

from scraping.apk_info import extract_apk_info

from apk.model import ABigModel, APDModel, ExodusModel

def main(args):
    """
    Analyse a single APK file with the models 
    """
    if len(ags) < 1:
        print(f"missing path to APK")
        sys.exit(1)

    apk_path = args[1]

    info = extract_apk_info(apk_path)

    perms = info['permissions']
    cats = info['categories']

    # print(perms, cats)

    # model = ABigModel("out/abig_ae.keras")
    model = APDModel("out/apd_vae.keras")
    # model = ExodusModel("out/exodus_vae.keras")
    res = model.analyse_apk(perms, cats)
    print(res)

    models = [
        APDModel("out/apd_ae.keras"),
        ExodusModel("out/exodus_ae.keras"),
        ABigModel("out/abig_ae.keras"),
        APDModel("out/apd_vae.keras"),
        ExodusModel("out/exodus_vae.keras"),
        ABigModel("out/abig_vae.keras"),
        APDModel("out/apd_sae.keras"),
        ABigModel("out/abig_sae.keras"),
        ExodusModel("out/exodus_sae.keras"),
    ]

if __name__ == "__main__":
    main(sys.argv[1:])
