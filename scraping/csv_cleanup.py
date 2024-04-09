import matplotlib.pyplot as plt
import pandas as pd

import heuristics

# Calculate the proportion to filter out (e.g., 80%)
IGNORE_LEAST_COMMON_PERCENT = 0.99  # Change this to the desired proportion (e.g., 0.10 for 10%)

# Read the CSV file into a Pandas DataFrame
file_path = 'data/zenodo-csv.csv'
df = pd.read_csv(file_path)

# Pre processing of names
df.iloc[:, 1] = df.iloc[:, 1].str.lower().str.replace('\s+', ' ', regex=True)

# Select boolean columns
boolean_columns = df.columns[2:]  # Assuming columns after 'ID' and 'Name' are not boolean

# Count the number of 'True' values in each boolean column
true_counts = df[boolean_columns].apply(lambda col: col.sum(), axis=0)

# Calculate the number of columns to filter out based on the proportion
num_to_filter = int(len(boolean_columns) * IGNORE_LEAST_COMMON_PERCENT)

# Filter out the columns with the least number of True values based on the proportion
sorted_counts = true_counts.sort_values(ascending=True)
filtered_columns = sorted_counts.head(num_to_filter).index
# df['OTHER_PERMISSIONS'] = df[filtered_columns].apply(lambda col: float(col.sum()+1) / num_to_filter, axis=1)  # .sum(axis=1)
df['OTHER_PERMISSIONS'] = df[filtered_columns].apply(lambda col: col.sum(), axis=1)  # .sum(axis=1)
filtered_df = df.drop(columns=filtered_columns)

# Recalculate true_counts after filtering
boolean_columns = filtered_df.columns[2:]
true_counts = filtered_df[boolean_columns].apply(lambda col: col.sum(), axis=0)
# print(true_counts.head())

# Sort the columns by the number of 'True' values
sorted_columns = true_counts.sort_values(ascending=False)

# Add a new 'Class' column with count of 'True' values in each row
# 0: normal
# 1: anomaly
# filtered_df['Class'] = filtered_df.apply(heuristics.heuristic, axis=1)
print("====================")
print(filtered_df.describe())

# anomaly_ratio = filtered_df['Class'].sum() / filtered_df.shape[0]

# Get additional information
num_final_columns = len(sorted_columns)
num_removed_columns = len(filtered_columns)
max_true_count = sorted_columns.max()
min_true_count = sorted_columns.min()

# Print the information
# print(f"Ratio of anomalies: {100 * anomaly_ratio}% of {filtered_df.shape[0]}")
print(f"Number of final columns shown: {num_final_columns}")
print(f"Number of removed permissions: {num_removed_columns}")
print(f"Maximum number of apps asking for permission: {max_true_count}")
print(f"Minimum number of apps asking for permission: {min_true_count}")

# Write the selected data to a new CSV file with appropriate headers
selected_columns = list(filtered_df.columns[:2]) + list(sorted_columns.index) # + ["Class"]
filtered_df.to_csv('data/selected_data.csv', columns=selected_columns, index=False)

# Plot the data
plt.figure(figsize=(10, 6))
sorted_columns.plot(kind='bar', color='skyblue')
plt.title('Number of apps asking for a permission')
plt.xlabel('Permission')
plt.ylabel('Number of permission requests')
plt.xticks(rotation=45)
plt.tight_layout()
plt.show()
