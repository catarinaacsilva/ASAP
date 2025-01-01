import polars as pl

COL_NAME = 'package'
# COL_NAME = 'id'

file_path = 'dataset/android_big.csv'           # Path to the CSV file
df = pl.read_csv(file_path)

def get_one_hot_columns(target_id):
    # Load the CSV file into a Polars DataFrame
    # df = pl.read_csv(file_path)
    
    # Ensure that the first column is 'id'
    # if df.columns[0] != COL_NAME:
    #     raise ValueError(f"The first column of the CSV should be '{COL_NAME}'.")
    
    # Check if the target ID exists in the DataFrame
    if target_id not in df[COL_NAME].to_list():
        raise ValueError(f"Package {target_id} not found in the dataset.")
    
    # Find the row corresponding to the target ID
    target_row = df.filter(pl.col(COL_NAME) == target_id).to_dicts()[0]
    
    # Find the columns where the value is 1
    one_hot_columns = [col for col, value in target_row.items() if value == 1 and col != COL_NAME and col != "class"]
    
    return one_hot_columns


# Example usage
if __name__ == "__main__":
    # file_path = 'dataset/android_big.csv'           # Path to the CSV file
    target_id = "com.google.android.marvin.talkback"  # The ID you are querying for

    # Get the columns where the value is 1 for the target_id
    columns_with_one = get_one_hot_columns(file_path, target_id)

    # Print the results
    print(f"Columns where value is 1 for package {target_id}: {columns_with_one}")
