from heuristics import heuristic_priv_new

import matplotlib.pyplot as plt
import pandas as pd

from sklearn.preprocessing import OneHotEncoder


# Calculate the proportion to filter out (e.g., 80%)
IGNORE_LEAST_COMMON_PERCENT = 0.99  # Change this to the desired proportion (e.g., 0.10 for 10%)

# Read the CSV file into a Pandas DataFrame
file_path = '../data/new/Better_Android_Permission.csv'
df = pd.read_csv(file_path)

# Pre processing of names
# df.iloc[:, 1] = df.iloc[:, 1].str.lower().str.replace('\s+', ' ', regex=True)
df = df.rename(str.lower, axis='columns')
print(df.columns)

# Select boolean columns
df = df.drop(columns=[
    'app',
    # 'package',
    # 'category',
    'rating',
    'number of ratings',
    'price',
    'related apps',
    'dangerous permissions count',
    'safe permissions count',
    'class',
])

MAX_CAT = None
one_hot_enc = OneHotEncoder(max_categories=MAX_CAT, sparse_output=False)

transformed = one_hot_enc.fit_transform(df['category'].to_numpy().reshape(-1, 1))
#Create a Pandas DataFrame of the hot encoded column
ohe_df = pd.DataFrame(transformed, columns=one_hot_enc.get_feature_names_out())
#concat with original data
df = pd.concat([df, ohe_df], axis=1).drop(['category'], axis=1)

# Add a new 'Class' column with count of 'True' values in each row
# 0: normal
# 1: anomaly
# filtered_df['Class'] = filtered_df.apply(lambda row: 0.0 if row[boolean_columns].sum() > 1 else 1.0, axis=1)
df['class'] = df.apply(heuristic_priv_new, axis=1)
print("====================")
print(df.describe())

anomaly_ratio = df['class'].sum() / df.shape[0]

print(f"Anomaly ratio: {anomaly_ratio:.3}")

# Write the selected data to a new CSV file with appropriate headers
# selected_columns = list(df.columns[:2]) + ["class"]
df.to_csv('../data/new_selected_data.csv', index=False)

