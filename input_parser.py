import os, json
from schemas import InputText, InputTextMetadata, Paragraph


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
        

    def _parse_markdown(self, input_string: str) -> list[InputText]:
        '''
        Parses input data from a markdown string.
        '''
        headline = None
        paragraphs = []
        current_subheadline = None
        current_text = []
        for line in input_string.splitlines():
            if line.startswith('# '):
                headline = line[2:].strip()
            elif line.startswith('## '):
                if current_text:
                    paragraphs.append(
                        Paragraph(
                            subheadline=current_subheadline,
                            text='\n'.join(current_text).strip()
                        )
                    )
                    current_text = []
                current_subheadline = line[3:].strip()
            elif line.strip() == '':
                if current_text:
                    paragraphs.append(
                        Paragraph(
                            subheadline=current_subheadline,
                            text='\n'.join(current_text).strip()
                        )
                    )
                    current_text = []
                    current_subheadline = None
            else:
                current_text.append(line)
        # Add any remaining text as a paragraph
        if current_text:
            paragraphs.append(
                Paragraph(
                    subheadline=current_subheadline,
                    text='\n'.join(current_text).strip()
                )
            )
        return [
            InputText(
                metadata=InputTextMetadata(),
                headline=headline,
                body=paragraphs
            )
        ]
    

    def _parse_text(self, input_string: str) -> list[InputText]:
        '''
        Parses input data from a text string.
        '''
        return [
            InputText(
                metadata=InputTextMetadata(),
                body=[Paragraph(text=input_string)]
            )
        ]


    def parse(self, file_path: str) -> list[InputText]:
        '''
        Runs the input parser based on the input type.

        Args:
            - file_path: The path to the input file. Either a file or a directory.
        '''
        if os.path.isfile(file_path):
            with open(file_path, 'r', encoding='utf-8') as file:
                if file_path.endswith('.json'):
                    return self._parse_json(file.read())
                elif file_path.endswith('.md'):
                    return self._parse_markdown(file.read())
                elif file_path.endswith('.txt'):
                    return self._parse_text(file.read())
                else:
                    raise ValueError('Unsupported file type')
        else:
            input_texts = []
            for entry in os.listdir(file_path):
                full_path = os.path.join(file_path, entry)
                if not os.path.isfile(full_path):
                    continue
                with open(full_path, 'r', encoding='utf-8') as file:
                    if entry.endswith('.json'):
                        input_texts.extend(self._parse_json(file.read()))
                    elif entry.endswith('.md'):
                        input_texts.extend(self._parse_markdown(file.read()))
                    elif entry.endswith('.txt'):
                        input_texts.extend(self._parse_text(file.read()))
                    else:
                        continue
            return input_texts
