import pandas as pd
import matplotlib.pyplot as plt

def plot_permissions_graph(csv_file, n_percent):
    # Read the CSV file
    df = pd.read_csv(csv_file)

    # Calculate the total number of apps for each permission
    permission_counts = df.iloc[:, 1:].sum().sort_values(ascending=False)

    # Print the number of apps for each permission
    print("Number of apps for each permission:")
    print(permission_counts)

    # Calculate the number of permissions to ignore
    n_to_ignore = int(len(permission_counts) * (n_percent / 100))

    # Identify the least used permissions
    least_used_permissions = permission_counts.index[:n_to_ignore]

    # Remove the least used permissions from the original DataFrame
    filtered_df = df.drop(columns=least_used_permissions)

    # Write the filtered DataFrame to a new CSV file
    filtered_df.to_csv('filtered_permissions_table.csv', index=False)

    # Prepare data for plotting
    filtered_permission_counts = filtered_df.iloc[:, 1:].sum().sort_values(ascending=False)

    # Plotting
    plt.figure(figsize=(10, 6))
    filtered_permission_counts.plot(kind='bar', color='skyblue')
    plt.title('Permissions Usage Across Apps')
    plt.xlabel('Permissions')
    plt.ylabel('Number of Apps')
    plt.xticks(rotation=45)
    plt.grid(axis='y')

    # Show the plot
    plt.tight_layout()
    plt.show()

# Example usage
csv_file_path = 'dataset/android_app_permission_dataset.csv'  # Change this to your CSV file path
n = 60  # Percentage of least used permissions to ignore
plot_permissions_graph(csv_file_path, n)
