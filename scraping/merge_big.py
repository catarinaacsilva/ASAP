import pandas as pd
import heuristics

# Load the CSV files
file1_path = 'filtered_permissions_table.csv'
file2_path = 'data/new_app_cats.csv'

# Read the CSV files into DataFrames
df1 = pd.read_csv(file1_path)
df2 = pd.read_csv(file2_path)
print(f"perms: {df1.shape} cats: {df2.shape}")

# Remove the "Key" column from both DataFrames (if it exists)
#df1 = df1.drop(columns=["Key"], errors='ignore')
#df2 = df2.drop(columns=["Key"], errors='ignore')

# Merge the DataFrames on the first column (the unique identifier)
# Assuming the unique identifier is still the first column of both DataFrames
merged_df = pd.merge(df1, df2, how='inner', left_on=df1.columns[0], right_on=df2.columns[0])
merged_df = merged_df.drop(columns=["Key"], errors='ignore')

# Save the merged DataFrame to a new CSV file (before adding the class column)
merged_file_path = 'merged_temp.csv'
merged_df.to_csv(merged_file_path, index=False)
print(f"Merged DataFrame saved to {merged_file_path}")

## Re-read the merged file
#merged_df = pd.read_csv(merged_file_path)
#
## Add the "class" column by applying the heuristic function
#merged_df['class'] = merged_df.apply(heuristics.heuristic, axis=1)
#print(f"Final: {merged_df.shape}")
#
## Save the final DataFrame with the class column
#final_output_path = 'merged_output_with_class.csv'
#merged_df.to_csv(final_output_path, index=False)
#
#print(f'Final DataFrame saved to {final_output_path}')

