import pandas as pd
import numpy as np
import os

def create_and_save_csv(path:str):
    # Define the number of rows
    num_rows = 500
    
    # Create the DataFrame with the specified uniform distributions
    data = {
        'A': np.random.randint(1, 17, num_rows),
        'B': np.random.randint(1, 19, num_rows),
        'C': np.random.randint(1, 14, num_rows),
        'D': np.random.randint(1, 12, num_rows)
    }
    
    df = pd.DataFrame(data)
    
    # Ensure the directory exists
    # os.makedirs('/presets/random', exist_ok=True)
    
    # Define the file path
    file_path = f'presets/random/{path}.csv'
    # Save the DataFrame to a CSV file
    df.to_csv(file_path, index=False)

    print(f"Data saved to {file_path}")



if __name__ == "__main__":
    for i in range(1, 101):
        create_and_save_csv(str(i))
