import pandas as pd

# Load the CSV file
df = pd.read_csv('Datasets/General/Better_Android_Permission.csv')

# Convert the 'Rating' and 'Number of ratings' columns to numeric types
df['Rating'] = pd.to_numeric(df['Rating'], errors = 'coerce')
df['Number of ratings'] = pd.to_numeric(df['Number of ratings'], errors = 'coerce')

# Remove rows with null values in the 'Rating' or 'Number of ratings' columns
df = df.dropna(subset = ['Rating', 'Number of ratings'])

# Calculate the metric 'Number of ratings / Rating'
df['Metric'] = df['Number of ratings'] / df['Rating']

# Initialize an empty DataFrame to store the results
top_10_by_category = pd.DataFrame()

# Iterate over each category
for category in df['Category'].unique():
    # Filter by category and sort by the metric in descending order
    df_category = df[df['Category'] == category].sort_values(
        by = 'Metric', ascending=False
    )
    
    # Select the top 10 unique applications
    top_10_category = df_category.drop_duplicates(subset = 'App').head(20)
    
    # Add to the main DataFrame
    top_10_by_category = pd.concat([top_10_by_category, top_10_category])

# Save the results to a CSV file
top_10_by_category.to_csv('Datasets/Top_20/top_20_by_category_metric.csv', index = False)

# Display the result
print(top_10_by_category[['App', 'Category', 'Rating', 'Number of ratings', 'Metric']])