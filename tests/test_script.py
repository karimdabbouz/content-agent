import json
import sys
import time
from pathlib import Path
from pydantic_ai import Agent
import tiktoken

# Add parent directory to Python path so we can import from the main codebase
sys.path.append(str(Path(__file__).parent.parent))

from schemas import InputText, OutputText
from system_prompts import from_file_system_prompt
from input_parser import InputParser
from dotenv import load_dotenv

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

def test_scenario(scenario_name, agent_kwargs, user_prompt):
    """Run a single test scenario"""
    # Load input
    parser = InputParser()
    input_texts = parser.parse('example_inputs/inputs/buergeramt-pillar')
    
    # Create the prompt that will be sent to the model
    full_prompt = {
        'user_prompt': user_prompt,
        'input_texts': [x.model_dump() for x in input_texts]
    }
    
    # Initialize the agent with the given settings
    agent = Agent(**agent_kwargs)
    
    # Create a serializable version of agent_kwargs
    serializable_kwargs = agent_kwargs.copy()
    serializable_kwargs['output_type'] = str(agent_kwargs['output_type'])
    
    # Convert the full prompt to JSON string (what actually gets sent to the model)
    full_prompt_json = json.dumps(full_prompt, default=str)
    
    # Count input tokens and words
    input_tokens = count_tokens(full_prompt_json, agent_kwargs['model'])
    input_words = count_words(full_prompt_json)
    
    # Run the model and save what comes back
    response = agent.run_sync(full_prompt_json)
    
    # Convert response to JSON string for counting
    response_json = json.dumps(response.output.model_dump(), ensure_ascii=False)
    
    # Count output tokens and words
    output_tokens = count_tokens(response_json, agent_kwargs['model'])
    output_words = count_words(response_json)
    
    # Save what we're about to send to the model (use default=str to handle datetime)
    with open(f'test_results/{scenario_name}.json', 'w') as f:
        json.dump({
            'scenario': scenario_name,
            'agent_settings': serializable_kwargs,
            'user_prompt': full_prompt,
            'metrics': {
                'input_tokens': input_tokens,
                'input_words': input_words,
                'output_tokens': output_tokens,
                'output_words': output_words
            }
        }, f, indent=2, default=str, ensure_ascii=False)
    
    with open(f'test_results/{scenario_name}.json', 'a') as f:
        f.write('\n\n--- MODEL OUTPUT ---\n\n')
        json.dump(response.output.model_dump(), f, indent=2, ensure_ascii=False)
    
    print(f"Completed scenario: {scenario_name}")
    print(f"Input: {input_words} words, {input_tokens} tokens")
    print(f"Output: {output_words} words, {output_tokens} tokens")

def main():
    user_prompt = "I want you to create a very long and detailed seo content piece from the input texts. The resulting text should serve as a pillar content piece and be in German. It should take all the information from the input texts and use it to deliver as much and as dense information as possible. The text must have 1000 words and be very detailed."
    
    # Test different configurations without assumptions about what they do
    test_configs = [
        # ("openai_baseline_no_limits", {}),
        # ("openai_output_tokens_only_2000", {'response_tokens_limit': 2000}),
        # ("openai_output_tokens_only_3000", {'response_tokens_limit': 3000}),
        # ("openai_max_completion_2000", {'max_completion_tokens': 2000}),
        # ("openai_max_completion_3000", {'max_completion_tokens': 3000}),
        # ("openai_total_context_30k_output_2k", {
        #     'max_tokens': 30000,  # Total context: room for ~21k input + more
        #     'max_completion_tokens': 2000
        # }),
        # ("openai_total_context_50k_output_3k", {
        #     'max_tokens': 50000,  # Very generous total context
        #     'max_completion_tokens': 3000
        # }),
        # ("openai_all_generous_limits", {
        #     'response_tokens_limit': 3000,
        #     'max_completion_tokens': 3000,
        #     'max_tokens': 50000  # Large enough for input + output
        # }),
        ("anthropic_baseline", {'model': 'anthropic:claude-3-haiku-20240307'}),
        ("anthropic_max_completion_2000", {
            'model': 'anthropic:claude-3-haiku-20240307',
            'max_completion_tokens': 2000
        }),
        ("anthropic_response_limit_2000", {
            'model': 'anthropic:claude-3-haiku-20240307',
            'response_tokens_limit': 2000
        }),
    ]
    
    for scenario_name, kwargs in test_configs:
        print(f"Testing scenario: {scenario_name}")
        try:
            test_scenario(scenario_name, {
                'model': 'openai:gpt-4o-mini',
                'system_prompt': from_file_system_prompt,
                'output_type': OutputText,
                **kwargs  # Add the test parameters
            }, user_prompt)
            print(f"✓ {scenario_name} completed successfully")
        except Exception as e:
            print(f"✗ {scenario_name} failed: {e}")
        time.sleep(35)
        print("-" * 50)

if __name__ == '__main__':
    main()