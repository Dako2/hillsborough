import json

def convert_json_to_jsonl(json_file_path, jsonl_file_path):
    with open(json_file_path, 'r') as json_file:
        data = json.load(json_file)
    print(data[0])
    
    with open(jsonl_file_path, 'w') as jsonl_file:
        for item in data:
            # Use jsonl library to write jsonl file
            jsonl_file.write(json.dumps({"text": "[INST] " + item["text"] + " [/INST]"}, ensure_ascii=False) + '\n')

# Usage example
json_file_path = 'hackathon_xingyuanlin_all_data.json' #'ju_hackathon_train_data.json'
jsonl_file_path = 'hackathon_xingyuanlin_all_data.jsonl'
convert_json_to_jsonl(json_file_path, jsonl_file_path)