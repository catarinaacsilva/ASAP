import csv
import json

with open('exodusNoIcon.json') as f:
    data = json.loads(f.read())

plist = set()

for app in data:
    for p in data[app]["Permissions"]:
        plist.add(p)

plist = sorted(list(plist))

data = [
    (data[d]["Id"], data[d]["Name"], *[float(p in data[d]["Permissions"]) for p in plist])
    for d in data
]

with open("zenodo-csv.csv", 'w') as f:
    csv_w = csv.writer(f, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
    csv_w.writerow(["Id", "Name", *plist])
    csv_w.writerows(data)
