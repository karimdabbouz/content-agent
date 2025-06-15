import os
import json
from pathlib import Path
from typing import Optional, List
from pydantic import BaseModel
from pydantic_ai import Agent
import tiktoken
from dotenv import load_dotenv
import sys
from datetime import datetime

# Add parent directory to Python path
sys.path.append(str(Path(__file__).parent.parent))

from schemas import InputText, OutputText
from system_prompts import from_file_system_prompt
from input_parser import InputParser

# Load environment variables
load_dotenv(dotenv_path=Path(__file__).parent.parent / '.env')

def count_tokens(text: str, model: str) -> int:
    """Count tokens for a given text using the appropriate tokenizer."""
    try:
        if model.startswith('openai:'):
            model_name = model.split(':')[1]
            enc = tiktoken.encoding_for_model(model_name)
        elif model.startswith('anthropic:'):
            # Anthropic uses a different tokenizer, but we can use GPT-4 as an approximation
            enc = tiktoken.encoding_for_model('gpt-4')
        else:
            raise ValueError(f"Unsupported model: {model}")
        return len(enc.encode(text))
    except Exception as e:
        print(f"Error counting tokens: {e}")
        return 0

def count_words(text: str) -> int:
    """Count words in a text."""
    return len(text.split())

def _construct_prompt(input_texts: List[InputText], user_prompt: str):
    """Construct the prompt in the same way as our SummarizerAgent."""
    user_prompt = {
        'user_prompt': user_prompt,
        'input_texts': [x.model_dump() for x in input_texts]
    }
    return json.dumps(user_prompt, indent=2, default=str)

def save_test_results(test_num: int, results: dict, input_texts: List[InputText], system_prompt: str):
    """Save test results to a JSON file."""
    # Create results directory if it doesn't exist
    results_dir = Path(__file__).parent / 'test_results'
    results_dir.mkdir(exist_ok=True)
    
    # Create timestamp-based directory for this test run
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    test_dir = results_dir / f'test_{timestamp}'
    test_dir.mkdir(exist_ok=True)
    
    # Save test results
    result_file = test_dir / f'test_{test_num}_results.json'
    
    # Convert datetime objects to strings in input_texts
    input_texts_data = []
    for text in input_texts:
        text_dict = text.model_dump()
        if text_dict['metadata']['created_at']:
            text_dict['metadata']['created_at'] = text_dict['metadata']['created_at'].isoformat()
        input_texts_data.append(text_dict)
    
    with open(result_file, 'w', encoding='utf-8') as f:
        json.dump({
            'input_texts': input_texts_data,
            'system_prompt': system_prompt,
            'user_prompt': results['settings'].get('user_prompt', ''),
            'metrics': {
                'input_tokens': results['input_tokens'],
                'input_words': results['input_words'],
                'output_tokens': results['output_tokens'],
                'output_words': results['output_words']
            },
            'settings': results['settings'],
            'output': results['response']
        }, f, indent=2, ensure_ascii=False)

def test_agent(
    model_name: str,
    input_texts: List[InputText],
    system_prompt: str,
    user_prompt: str,
    response_tokens_limit: Optional[int] = None,
    max_completion_tokens: Optional[int] = None,
    temperature: float = 0.7
) -> dict:
    """Test PydanticAI Agent with different settings and log metrics."""
    
    # Initialize agent with given settings
    agent_kwargs = {
        'model': model_name,
        'system_prompt': system_prompt,
        'output_type': OutputText,
        'temperature': temperature
    }
    
    # Add token limit settings
    if response_tokens_limit is not None:
        agent_kwargs['response_tokens_limit'] = response_tokens_limit
    if max_completion_tokens is not None:
        agent_kwargs['max_completion_tokens'] = max_completion_tokens
    
    agent = Agent(**agent_kwargs)
    
    # Construct the full prompt with input texts
    full_prompt = _construct_prompt(input_texts, user_prompt)
    
    # Count input tokens and words
    input_tokens = count_tokens(full_prompt, model_name)
    input_words = count_words(full_prompt)
    
    # Run the agent with the full prompt
    response = agent.run_sync(full_prompt)
    
    # Convert response to string for counting
    response_str = json.dumps(response.output.model_dump(), ensure_ascii=False)
    
    # Count output tokens and words
    output_tokens = count_tokens(response_str, model_name)
    output_words = count_words(response_str)
    
    # Return metrics
    return {
        'input_tokens': input_tokens,
        'input_words': input_words,
        'output_tokens': output_tokens,
        'output_words': output_words,
        'response': response.output.model_dump(),
        'settings': {
            'model_name': model_name,
            'response_tokens_limit': response_tokens_limit,
            'max_completion_tokens': max_completion_tokens,
            'temperature': temperature,
            'user_prompt': user_prompt
        }
    }

def main():
    # Load example input
    input_parser = InputParser()
    input_texts = input_parser.parse('example_inputs/example_input.json')
    
    user_prompt = """Summarize in one sentence"""
    
    # Test with different settings
    results = []
    
    # Test 1: Default settings (no limits)
    results.append(test_agent(
        model_name='openai:gpt-4o-mini',
        input_texts=input_texts,
        system_prompt=from_file_system_prompt,
        user_prompt=user_prompt
    ))
    
    # Test 2: response_tokens_limit for 1000 words (≈1500 tokens)
    results.append(test_agent(
        model_name='openai:gpt-4o-mini',
        input_texts=input_texts,
        system_prompt=from_file_system_prompt,
        user_prompt=user_prompt,
        response_tokens_limit=1500
    ))
    
    # Save results for each test
    for i, result in enumerate(results, 1):
        save_test_results(i, result, input_texts, from_file_system_prompt)
        print(f"\nTest {i}:")
        print(f"Model: {result['settings']['model_name']}")
        print(f"Input tokens: {result['input_tokens']}")
        print(f"Input words: {result['input_words']}")
        print(f"Output tokens: {result['output_tokens']}")
        print(f"Output words: {result['output_words']}")
        print("Settings:")
        for key, value in result['settings'].items():
            print(f"  {key}: {value}")

if __name__ == '__main__':
    main() 