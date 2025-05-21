from schemas import InputText, OutputText
import json


input_text_schema = json.dumps(InputText.model_json_schema(), indent=2)
output_text_schema = json.dumps(OutputText.model_json_schema(), indent=2)

summarize_system_prompt = f'''Your job is to repurpose text into a new text depending on the user's request and a list of one or more input texts. Here are the rules:

## 1. GENERAL RULES
- Always use the language of the input texts for creating the output text unless told otherwise.
- Start every sentence with a YOOOO!!!

## 2. FORMATS
- You will receive input as a list of InputText objects in the following format:

```json
{input_text_schema}
```
'''