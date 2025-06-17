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

def test_direct_openai(scenario_name: str, max_tokens: int, user_prompt: str, input_texts: list):
    """Test OpenAI directly without PydanticAI"""
    
    # Create the full prompt using the same format as PydanticAI test
    full_prompt = {
        'user_prompt': user_prompt,
        'input_texts': input_texts
    }
    
    # Count input tokens
    input_tokens = count_tokens(json.dumps(full_prompt))
    input_words = count_words(json.dumps(full_prompt))
    
    # Initialize OpenAI client
    client = OpenAI()
    
    try:
        # Convert full_prompt to JSON string
        full_prompt_json = json.dumps(full_prompt)
        
        # Make the API call
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": from_file_system_prompt},
                {"role": "user", "content": full_prompt_json}
            ],
            max_tokens=max_tokens,
            temperature=0.7
        )
        
        # Extract response
        output_text = response.choices[0].message.content
        
        # Count output tokens and words
        output_tokens = count_tokens(output_text)
        output_words = count_words(output_text)
        
        # Calculate total tokens used (from API response)
        usage = response.usage
        total_tokens_used = usage.total_tokens
        actual_input_tokens = usage.prompt_tokens
        actual_output_tokens = usage.completion_tokens
        
        # Save results
        results = {
            'scenario': scenario_name,
            'settings': {
                'model': 'gpt-4o-mini',
                'max_tokens': max_tokens,
                'temperature': 0.7
            },
            'input_analysis': {
                'calculated_input_tokens': input_tokens,
                'calculated_input_words': input_words,
                'api_input_tokens': actual_input_tokens
            },
            'output_analysis': {
                'calculated_output_tokens': output_tokens,
                'calculated_output_words': output_words,
                'api_output_tokens': actual_output_tokens
            },
            'api_usage': {
                'prompt_tokens': actual_input_tokens,
                'completion_tokens': actual_output_tokens,
                'total_tokens': total_tokens_used
            },
            'finish_reason': response.choices[0].finish_reason
        }
        
        # Save results to file
        with open(f'test_results/direct_openai_{scenario_name}.json', 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        
        # Save the actual output text
        with open(f'test_results/direct_openai_{scenario_name}_output.txt', 'w', encoding='utf-8') as f:
            f.write(output_text)
        
        print(f"✓ Direct OpenAI test '{scenario_name}' completed")
        print(f"  Input: {input_words} words, {actual_input_tokens} tokens (API count)")
        print(f"  Output: {output_words} words, {actual_output_tokens} tokens (API count)")
        print(f"  Finish reason: {response.choices[0].finish_reason}")
        print(f"  Max tokens requested: {max_tokens}")
        
        return results
        
    except Exception as e:
        print(f"✗ Direct OpenAI test '{scenario_name}' failed: {e}")
        return None

def main():
    parser = InputParser()
    input_texts = parser.parse('example_inputs/inputs/buergeramt-pillar')
    input_texts_dicts = [x.model_dump() for x in input_texts]

    user_prompt = "I want you to create a very long and detailed seo content piece from the input texts. The resulting text should serve as a pillar content piece and be in German. It should take all the information from the input texts and use it to deliver as much and as dense information as possible. The text must have 1000 words and be very detailed."

    full_prompt = {
        'user_prompt': user_prompt,
        'input_texts': input_texts_dicts
    }
    full_prompt_json = json.dumps(full_prompt, ensure_ascii=False)

    client = OpenAI()
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": from_file_system_prompt},
            {"role": "user", "content": full_prompt_json}
        ],
        temperature=0.7
    )

    output_text = response.choices[0].message.content
    print(output_text)

if __name__ == '__main__':
    main() 