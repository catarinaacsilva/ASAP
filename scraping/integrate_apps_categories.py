import csv

perms = {}
cats = {}

perms_h = None
cats_h = None

actual_apps = []

with open('data/selected_data.csv') as csvfile:
    reader = csv.reader(csvfile)
    for row in reader:
        actual_apps.append(row[1].lower())
        perms[row[1].lower()] = row[2:]
perms_h = perms["name"]
actual_apps = set(actual_apps[1:])
print(perms_h)

scraped_categories = []

with open('data/new_app_cats.csv') as csvfile:
    reader = csv.reader(csvfile)
    for row in reader:
        scraped_categories.append(row[0].lower())
        cats[row[0].lower()] = row[1:]
cats_h = cats["key"]
scraped_categories = scraped_categories[1:]
print(cats_h)
#print(actual_apps[:5])
#print(scraped_categories[:5])
s = [app for app in scraped_categories if app in actual_apps]
print(len(actual_apps), len(scraped_categories), len(s))

with open('data/perms_cats_tmp.csv', 'w') as csv_file:
    csv_writer = csv.writer(csv_file)

    csv_writer.writerow(["Name", *cats_h, *perms_h])
    for app in s:
        csv_writer.writerow([app, *cats[app], *perms[app]])

import pandas as pd

import heuristics

df = pd.read_csv('data/perms_cats_tmp.csv')

df['Class'] = df.apply(heuristics.heuristic, axis=1)

print("====================")
print(df.describe())

anomaly_ratio = df['Class'].sum() / df.shape[0]
print(f"Ratio of anomalies: {100 * anomaly_ratio}% of {df.shape[0]}")

df.to_csv('data/perms_cats.csv', index=False)