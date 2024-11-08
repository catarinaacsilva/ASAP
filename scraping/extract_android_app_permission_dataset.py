# From dataset https://www.kaggle.com/datasets/gauthamp10/app-permissions-android

import json
import csv

import polars as pl

def extract_csv_from_origin():
    with open('googleplay-app-permission.json') as f:
        data = json.loads(f.read())

    permissions = set()
    for app in data:
        for p in app['allPermissions']:
            permissions.add(p['permission'])
    permissions = list(permissions)

    head = ["package", *permissions]

    csv_data = []
    for app in data:
        app_perms = [p["permission"] for p in app["allPermissions"]]
        app_row = [app["appId"]]

        for perm in permissions:
            app_row.append(1 if perm in app_perms else 0)

        csv_data.append(app_row)

    
    with open("dataset/android_app_permission_dataset.csv", 'w', newline='') as csv_file:
        csv_writer = csv.writer(csv_file)
        csv_writer.writerow(head)

        # Write rows with one-hot encoding
        lns = 0
        for ln in csv_data:
            csv_writer.writerow(ln)
            lns += 1
        print(f"Written {lns} lines")

def merge_with_categories():
    # Read the CSV files
    df1 = pl.read_csv("dataset/android_app_permission_dataset.csv")
    df2 = pl.read_csv("data/new_app_cats.csv")

    # Merge the two DataFrames on the first column (ID)
    merged_df = df1.join(df2, left_on=df1.columns[0], right_on=df2.columns[0], how='outer')

    # Write the merged DataFrame to a new CSV file
    merged_df.write_csv(output_file)



if __name__ == "__main__":
    extract_csv_from_origin()