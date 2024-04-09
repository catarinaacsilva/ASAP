import pandas as pd

# Your dataset
df_media = pd.read_csv('Datasets/Top_20/heuristics_results_class_20.csv')

# One-hot encoding
df_encoded = pd.get_dummies(df_media, columns=['Category'], drop_first = False)

# Replace True/False with 1/0
df_encoded.replace({True: 1, False: 0}, inplace=True)

# Move the 'Class' column to the end
df_encoded = pd.concat([df_encoded.drop('Class', axis = 1), df_encoded[['Class']]], axis = 1)

# Save the resulting DataFrame to a CSV file
df_encoded.to_csv('one-hot_class_20.csv', index = False)

# Display the resulting DataFrame
print(df_encoded)