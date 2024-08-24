import csv
from io import StringIO

def string_to_csv(input_string, output_filename):
    # Split the input string into lines
    lines = input_string.strip().split('\n')
    
    # Split each line into values
    data = [line.split(',') for line in lines]
    
    # Write the data to a CSV file
    with open(output_filename, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerows(data)
    
    print(f"CSV file '{output_filename}' has been created.")

# Example usage
input_str = """Name,Age,City
John,30,New York
Alice,25,Los Angeles
Bob,35,Chicago"""

string_to_csv(input_str, 'output.csv')


import csv

def get_column_names(csv_file):
    """
    Gets the list of column names from a CSV file.

    Args:
        csv_file (str): The path to the CSV file.

    Returns:
        list: A list of column names.
    """

    with open(csv_file, 'r') as file:
        reader = csv.reader(file)
        header = next(reader)  # Read the first row (header)
        print(header)
        return header
    
get_column_names('output.csv')