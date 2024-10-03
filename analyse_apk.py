import gzip
import tensorflow as tf
import numpy as np
import polars as pl
import tensorflow.keras.backend as K
from tqdm.keras import TqdmCallback

from scraping.apk_info import extract_apk_info

APD_PERMISSIONS = [
    "OTHER_PERMISSIONS",
    "INTERNET",
    "ACCESS_NETWORK_STATE",
    "WAKE_LOCK",
    "WRITE_EXTERNAL_STORAGE",
    "RECEIVE",
    "READ_EXTERNAL_STORAGE",
    "ACCESS_WIFI_STATE",
    "VIBRATE",
    "RECEIVE_BOOT_COMPLETED",
    "BIND_GET_INSTALL_REFERRER_SERVICE",
    "ACCESS_FINE_LOCATION",
    "BILLING",
    "C2D_MESSAGE",
    "ACCESS_COARSE_LOCATION",
    "CAMERA",
    "READ_PHONE_STATE",
    "GET_ACCOUNTS",
    "FOREGROUND_SERVICE",
    "WRITE_SETTINGS",
    "BLUETOOTH",
    "RECORD_AUDIO",
    "READ_CONTACTS",
    "READ_GSERVICES",
    "SYSTEM_ALERT_WINDOW",
    "CHANGE_WIFI_STATE",
    "READ_SETTINGS",
    "READ",
    "MODIFY_AUDIO_SETTINGS",
    "WRITE",
    "BROADCAST_BADGE",
    "UPDATE_SHORTCUT",
    "USE_CREDENTIALS",
    "BLUETOOTH_ADMIN",
    "UPDATE_COUNT",
    "UPDATE_BADGE",
    "USE_FINGERPRINT",
    "CHANGE_BADGE",
    "GET_TASKS",
    "PROVIDER_INSERT_BADGE",
    "READ_APP_BADGE",
    "INSTALL_SHORTCUT",
    "MANAGE_ACCOUNTS",
]

def coeff_determination(y_true, y_pred):
    SS_res =  K.sum(K.square( y_true-y_pred ))
    SS_tot = K.sum(K.square( y_true - K.mean(y_true) ) )
    return ( 1 - SS_res/(SS_tot + K.epsilon()) )


def isodata(array: np.ndarray) -> float:
    """
    Returns optimal threshold for dividing the sequence of values.

    Args:
        array (np.ndarray): numpy array with the values
    
    Returns:
        float: optimal threshold for dividing the sequence of values
    """
    median = np.median(array)
    print(median, array)
    previous_median = 0.0 
    
    while median != previous_median:
        median_left = np.median(array[array <= median])
        median_right = np.median(array[array > median])

        previous_median = median
        median = (median_left+median_right) / 2.0

    return median


def mad_score(points):
    m = np.median(points)
    ad = np.abs(points - m)
    mad = np.median(ad)
    return 0.6745 * ad / mad


def main(model: str, path: str, to_drop: [str]):
    with gzip.open(path,'rb') as f:
        file_content=f.read()
    df = pl.read_csv(file_content)

    df = df.rename({col: col.lower() for col in df.columns})
    df = df.rename({'class': 'label'})
    if 'package' in df.columns: # deal with null values
        df = df.filter(pl.col('package').is_not_null())

    df_clean = df.drop(to_drop)
    
    autoencoder = tf.keras.models.load_model(f"out/ae_{model}.keras")

    print(df_clean.shape)
    X_test = np.zeros(shape=(1, df_clean.shape[1]-1), dtype=np.float32)
    y_test = np.zeros(shape=(1), dtype=np.float32)
    reconstructions = autoencoder.predict(X_test)

    mse = np.mean(np.power(X_test - reconstructions, 2), axis=1)
    mae = np.mean(np.abs(X_test - reconstructions), axis=1)

    malicious = mae[y_test==1]
    benign    = mae[y_test==0]

    print(f"{len(malicious)/(len(benign)+len(malicious)):.2}% anomaly")

    thr = 0.5 # 0.0597514188458294 # isodata(mae)
    print(f'ISO-Data Thr: {thr}')
    y_pred = mse > thr
    print(y_pred)


def convert_to_apd():
    pass


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(f"usage: python {sys.argv[0]} <path to apk>")
        sys.exit(1)

    apk_path = sys.argv[1]

    info = extract_apk_info(apk_path)
    app = info['permissions']

    print(len(APD_PERMISSIONS), len(app), len(list(e for e in app if e in APD_PERMISSIONS)))
    print(info['categories'])

#    for model, path, to_drop in (
#        ("apd", "dataset/android_permission_dataset.csv.gz", ("name")), 
#        ("exodus", "dataset/exodus.csv.gz", ("package")),
#        ):
#        main(model, path, to_drop)