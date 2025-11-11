from typing import Union, List, Dict, Optional
import pandas as pd
import os

def save_data(
        data: Union[pd.DataFrame, List[Dict]],
        filename: str,
        file_format: Optional[str] = None
) -> None:
    """
    Saves generic data(DataFrame or list of dicts) to a file.

    This utility function handles the conversion to a pandas DataFrame if the input
    is a list of dictionaries, infers the file format from the file filename if not explicitly 
    provided, and saves the data to the specified file path.

    Supported output formats: 'csv', 'json', 'excel', 'parquet'.

    Args:
        data (Union[pd.DataFrame, List[Dict]]): 
            The data to save, either as a pandas DataFrame or a list of dictionaries.
        filename (str): 
            The full path and name of the file to save (e.g., './output/my_data.csv').
            Intermediate directories will be created if they don't exist.
        file_format (Optional[str]): 
            The explicit file format to save as. Options: 'csv', 'json', 'excel', 'parquet'.
            If None, the format is inferred from the `filename`'s extension.
            If inference fails, it defaults to 'csv'.

    Raises:
        TypeError: 
            If the input `data` is not a pandas DataFrame or a list of dictionaries.
        ValueError: 
            If an unsupported `file_format` is specified.
        ImportError: 
            If a required dependency for a specific `file_format` (e.g., 'openpyxl' for Excel,
            'pyarrow' or 'fastparquet' for Parquet) is missing.
        Exception: 
            For any other errors encountered during the file saving process.

    """

    # Convert to DataFrame if needed
    if isinstance(data, list):
        df = pd.DataFrame(data)
    elif isinstance(data, pd.DataFrame):
        df = data
    else:
        raise TypeError("Input 'data' must be a pandas DataFrame or a list of dictionaries.")
    
    # Auto-detect file format
    if file_format is None:
        if filename.endswith('.csv'):
            file_format = 'csv'
        elif filename.endswith('.json'):
            file_format = 'json'
        elif filename.endswith(('.xlsx', '.xls')):
            file_format = 'excel'
        elif filename.endswith('.parquet'):
            file_format = 'parquet'
        else:
            file_format = 'csv'
    
    # Create dictionary if it doesn't exist
    output_dir = os.path.dirname(filename)
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir, exist_ok=True)

    print(f"Attempting to save {len(df)} records to {filename} as {file_format}...")

    # Save to file 
    try:
        if file_format == 'csv':
            df.to_csv(filename, index=False)
        elif file_format == 'json':
            df.to_json(filename, orient='records', indent=2)
        elif file_format == 'excel':
            df.to_excel(filename, index=False)
        elif file_format == 'parquet':
            df.to_parquet(filename, index=False)
        else:
            raise ValueError(f"Unsupported file format: '{file_format}'. Must be one of 'csv', 'json', 'excel', 'parquet'.")

        abs_path = os.path.abspath(filename)    
        print(f"Successfully saved {len(df)} records to {abs_path}")
        return abs_path

    except ImportError as e:
        print(f"Error: Missing dependency for format '{file_format}'. {e}")
        print(f"Please install required libraries: 'openpyxl' for Excel, 'pyarrow' or 'fastparquet' for Parquet.")
        # Re-raise to indicate that the save operation failed due to missing deps
        raise
    except Exception as e:
        print(f"Error saving file '{filename}': {e}")
        # Re-raise to indicate generic saving failure
        raise