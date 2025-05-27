import os, json
from schemas import InputText


class InputParser:
    '''
    Flexibly parse input data into a list of InputText objects for the summarizer agent.
    '''

    def _parse_json(self, input_string: str) -> list[InputText]:
        '''
        Parses input data from a JSON string.
        Handles one or more input texts, but doesn't currently handle malformed JSON.

        Args:
            - input_str: The JSON string to parse.
        '''
        try:
            input_data = json.loads(input_string)
            if isinstance(input_data, list):
                return [InputText.model_validate(x) for x in input_data]
            else:
                return [InputText.model_validate(input_data)]
        except json.JSONDecodeError:
            raise ValueError('Invalid JSON string')


    def parse(self, file_path: str) -> list[InputText]:
        '''
        Runs the input parser based on the input type.
        '''
        with open(file_path, 'r', encoding='utf-8') as file:
            if file_path.endswith('.json'):
                return self._parse_json(file.read())
            else:
                raise ValueError('Unsupported file type')
