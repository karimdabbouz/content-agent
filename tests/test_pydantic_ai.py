import os
import json
from pathlib import Path
from typing import Optional, List
from pydantic import BaseModel
from pydantic_ai import Agent
import tiktoken
from dotenv import load_dotenv
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
        'model_name': model_name,
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
    response_str = json.dumps(response.model_dump(), ensure_ascii=False)
    
    # Count output tokens and words
    output_tokens = count_tokens(response_str, model_name)
    output_words = count_words(response_str)
    
    # Return metrics
    return {
        'input_tokens': input_tokens,
        'input_words': input_words,
        'output_tokens': output_tokens,
        'output_words': output_words,
        'response': response.model_dump(),
        'settings': {
            'model_name': model_name,
            'response_tokens_limit': response_tokens_limit,
            'max_completion_tokens': max_completion_tokens,
            'temperature': temperature
        }
    }

def main():
    # Load example input
    input_parser = InputParser()
    input_texts = input_parser.parse('example_inputs/example_input.json')
    
    user_prompt = """Please generate a detailed response of at least 1000 words."""
    
    # Test with different settings
    results = []
    
    # Test 1: Default settings (no limits)
    results.append(test_agent(
        model_name='openai:gpt-4',
        input_texts=input_texts,
        system_prompt=from_file_system_prompt,
        user_prompt=user_prompt
    ))
    
    # Test 2: response_tokens_limit for 1000 words (≈1500 tokens)
    results.append(test_agent(
        model_name='openai:gpt-4',
        input_texts=input_texts,
        system_prompt=from_file_system_prompt,
        user_prompt=user_prompt,
        response_tokens_limit=1500
    ))
    
    # Test 3: response_tokens_limit for 1500 words (≈2250 tokens)
    results.append(test_agent(
        model_name='openai:gpt-4',
        input_texts=input_texts,
        system_prompt=from_file_system_prompt,
        user_prompt=user_prompt,
        response_tokens_limit=2250
    ))
    
    # Test 4: max_completion_tokens for 1000 words
    results.append(test_agent(
        model_name='openai:gpt-4',
        input_texts=input_texts,
        system_prompt=from_file_system_prompt,
        user_prompt=user_prompt,
        max_completion_tokens=1500
    ))
    
    # Test 5: Both limits set for 1000 words
    results.append(test_agent(
        model_name='openai:gpt-4',
        input_texts=input_texts,
        system_prompt=from_file_system_prompt,
        user_prompt=user_prompt,
        response_tokens_limit=1500,
        max_completion_tokens=1500
    ))
    
    # Print results
    for i, result in enumerate(results, 1):
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