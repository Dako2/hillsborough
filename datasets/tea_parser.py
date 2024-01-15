import csv
import json

filename = "./tea.csv"

# Open the CSV
with open(filename, 'r') as file:
    # Read the CSV and add data to a dictionary
    csv_reader = csv.DictReader(file)
    data = [row for row in csv_reader]

# Convert dictionary to JSON and write to a file
with open(filename[:-4]+'.json', 'w', encoding='utf-8') as json_file:
    json.dump(data, json_file, ensure_ascii=False, indent=4)
