import pandas as pd
import numpy as np

def find_1_percentile_threshold(csv_file):
    # Load the CSV file into a DataFrame
    df = pd.read_csv(csv_file)

    # Ensure the 'class' column exists
    if 'class' not in df.columns:
        raise ValueError("The CSV file must have a 'class' column.")

    # Get the 'class' column as a numpy array
    class_values = df['class'].values

    # Calculate the 1st percentile threshold
    threshold = np.percentile(class_values, 99)

    return threshold

def update_class_column(csv_file, threshold, output_file):
    # Load the CSV file into a DataFrame
    df = pd.read_csv(csv_file)

    # Update the 'class' column based on the threshold
    df['class'] = (df['class'] >= threshold).astype(int)

    # Save the modified DataFrame to a new CSV file
    df.to_csv(output_file, index=False)
    print(f"Updated CSV file saved as {output_file}")

# Example usage
csv_file = 'merged_output_with_class.csv'  # Replace this with the path to your CSV file
output_file = 'updated_file.csv'  # Path to save the updated CSV file

# Find the 1st percentile threshold
threshold = find_1_percentile_threshold(csv_file)

# Update the 'class' column and save the result
update_class_column(csv_file, threshold, output_file)
