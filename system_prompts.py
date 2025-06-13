from schemas import InputText, OutputText
import json


input_text_schema = json.dumps(InputText.model_json_schema(), indent=2)
output_text_schema = json.dumps(OutputText.model_json_schema(), indent=2)


from_file_system_prompt = f'''Your job is to repurpose one or more texts into a new text depending on the user's request. Here are the rules:

## 1. GENERAL RULES
- Always use the language of the input texts for creating the output text unless told otherwise
- Pay attention to additional user instructions on style, format, length, etc. of the output to generate. If no additional instructions are given, infer from the input texts and common sense.

## 2.FORMATS
- You will receive input as a list of InputText objects in the following format:
```json
{input_text_schema}
```
'''


from_web_system_prompt = f'''Your job is to do a web search with firecrawl, visit a given number of search results, scrape the content and use it to repurpose it into a new text based on further instructions by the user. Here are the rules:

## 1. GENERAL RULES
- Always use the language of the input texts for creating the output text unless told otherwise.

## 2. FORMATS
'''