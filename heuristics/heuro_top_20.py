import pandas as pd

# Upload CSV file
df_media = pd.read_csv('Datasets/Top_20/mean_permissions_by_category_metric_20.csv')
df_better = pd.read_csv('Datasets/General/Better_Android_Permission.csv')
df_result = pd.DataFrame() 

# Iterate over the rows of DataFrame df_better
for index, row in df_better.iterrows():
    # Find the corresponding category in the metric
    category_metric = df_media[df_media['Category'] == row['Category']]
    
    bad_permissions = []
    
    # Iterate over the columns of the current row in df_better
    for column_index, (column, value) in enumerate(row.items()):
        if column_index < 7 or column == 'Safe permissions count':
            continue
        
        category_value = category_metric[column].values[0]
        
        if column == 'Dangerous permissions count' and value > 8 or value - category_value > 5:
            # Concatenate the row to df_result
            bad_permissions.append(column)
            
        if value == 1 and category_value < 0.05:
            # Concatenate the row to df_result
            bad_permissions.append(column)
    
    # Add only the bad permissions to the csv file
    row['Anomaly'] = 0 if not bad_permissions else 1 
    
    # Drop headers
    columns_to_drop = [
        'App',
        'Rating', 
        'Number of ratings', 
        'Price', 
        'Related apps', 
        'Dangerous permissions count', 
        'Safe permissions count',
        'Class' 
    ]
    
    row = row.drop(columns_to_drop, errors = 'ignore')
    df_result = pd.concat([df_result, pd.DataFrame([row])], ignore_index = True)

# Rename the 'Anomaly' column to 'Class'
df_result = df_result.rename(columns={'Anomaly': 'Class'})

# Save the resulting DataFrame to a CSV file
df_result.to_csv('Datasets/Top_20/heuristics_results_class_20.csv', index = False)

# Display the resulting DataFrame
print(df_result)