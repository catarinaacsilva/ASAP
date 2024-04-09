import pandas as pd

# Load the CSV file
df = pd.read_csv('Datasets/Top_20/top_20_by_category_metric.csv')

# Select the columns of interest (from the start to the end of the header)
selected_columns = df.columns[df.columns.get_loc("Dangerous permissions count"):]

# Add the 'Category' column to the beginning of the selection
selected_columns = ['Category'] + selected_columns.tolist()

# Create a new DataFrame with the selected columns
df_selected = df[selected_columns]

# Convert the columns of dangerous permissions to numeric type
df_selected.iloc[:, 1:] = df_selected.iloc[:, 1:].apply(pd.to_numeric, errors = 'coerce')

def custom_mean(values):
    # Your custom logic for calculating the mean
    return values.mean(skipna = True)

# Calculate the mean by category
mean_permissions_by_category = df_selected.groupby('Category').agg(custom_mean).reset_index()

# Save the results to a CSV file
mean_permissions_by_category.to_csv('Datasets/Top_20/mean_permissions_by_category_metric_20.csv', index = False)

# Display the result
print(mean_permissions_by_category)