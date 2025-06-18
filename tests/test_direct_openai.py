import json
import os
import time
from pathlib import Path
from openai import OpenAI
import tiktoken
from dotenv import load_dotenv
import sys
# Add parent directory to Python path so we can import from the main codebase
sys.path.append(str(Path(__file__).parent.parent))

from system_prompts import from_file_system_prompt
from input_parser import InputParser

# Load environment variables
load_dotenv(dotenv_path=Path(__file__).parent.parent / '.env')

def count_tokens(text: str, model: str = "gpt-4o-mini") -> int:
    """Count tokens for a given text using the appropriate tokenizer."""
    try:
        enc = tiktoken.encoding_for_model(model)
        return len(enc.encode(text))
    except Exception as e:
        print(f"Error counting tokens: {e}")
        return 0

def count_words(text: str) -> int:
    """Count words in a text."""
    return len(text.split())

def load_input_files(input_dir: str) -> str:
    """Load all input files and combine them into one text."""
    input_path = Path(__file__).parent.parent / 'example_inputs' / 'inputs' / input_dir
    combined_text = ""
    
    for file_path in sorted(input_path.glob("*.txt")):
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read().strip()
            combined_text += content + "\n\n"
    
    return combined_text.strip()

def main():
    parser = InputParser()
    input_texts = parser.parse('example_inputs/inputs/buergeramt-pillar')
    input_texts_dicts = [x.model_dump() for x in input_texts]

    user_prompt = '''I want you to create a very long and detailed seo content piece from the input texts. The resulting text should serve as a pillar content piece and be in German. It should take all the information from the input texts and use it to deliver as much and as dense information as possible. The text must have 1000 words and be very detailed.'''

    full_prompt = {
        'user_prompt': user_prompt,
        'input_texts': input_texts_dicts
    }
    full_prompt_json = json.dumps(full_prompt, ensure_ascii=False)

    # Count input tokens and words (calculated)
    input_tokens = count_tokens(full_prompt_json)
    input_words = count_words(full_prompt_json)

    client = OpenAI()
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": from_file_system_prompt},
            {"role": "user", "content": full_prompt_json}
        ]
    )

    output_text = response.choices[0].message.content

    # Count output tokens and words (calculated)
    output_tokens = count_tokens(output_text)
    output_words = count_words(output_text)

    # API token usage
    usage = response.usage
    api_input_tokens = usage.prompt_tokens
    api_output_tokens = usage.completion_tokens
    api_total_tokens = usage.total_tokens

    # Print metrics
    print(f"Input: {input_words} words, {input_tokens} tokens (calculated), {api_input_tokens} tokens (API)")
    print(f"Output: {output_words} words, {output_tokens} tokens (calculated), {api_output_tokens} tokens (API)")
    print(f"Total tokens (API): {api_total_tokens}")
    print(f"Finish reason: {response.choices[0].finish_reason}")

    # Save results
    Path("test_results").mkdir(exist_ok=True)
    results = {
        'settings': {
            'model': 'gpt-4o-mini'
        },
        'input_analysis': {
            'calculated_input_tokens': input_tokens,
            'calculated_input_words': input_words,
            'api_input_tokens': api_input_tokens
        },
        'output_analysis': {
            'calculated_output_tokens': output_tokens,
            'calculated_output_words': output_words,
            'api_output_tokens': api_output_tokens
        },
        'api_usage': {
            'prompt_tokens': api_input_tokens,
            'completion_tokens': api_output_tokens,
            'total_tokens': api_total_tokens
        },
        'finish_reason': response.choices[0].finish_reason
    }
    with open('test_results/direct_openai_simple.json', 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    with open('test_results/direct_openai_simple_output.txt', 'w', encoding='utf-8') as f:
        f.write(output_text)

if __name__ == '__main__':
    main() 