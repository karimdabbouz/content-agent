# Summarizer Agent

The goal is to build an LLM agent that can accept one or n number of input texts and then flexibly rewrite them into a given format, i.e. a blog post, an article, a newsletter etc.

I want this to be as flexible and modular as possible in order to be able to integrate it into different workflows. I am therefore building the agent as an MCP client using PydanticAI that can connect to MCP servers either for receiving input and/or for sending output. Example workflow: Receive a number of weekly newsletters, repurpose them into a single article and create a draft in Wordpress. Or receive a number of newsletters and summarize them into a single one which is then sent to my mail address using a Gmail MCP server (who reads all those newsletters anyway?)

An agent can be seen as a combination of MCP servers for input and/or output and a system prompt. Hence, agents will be created at startup of the webserver and can then be used through their respective endpoints. They will live in memory and can be altered at runtime through the API. This should work for a small number of agents (running MCP servers is another story, but they will most likely be used by multiple agents anyway). Actions in the CLI app correspond to API endpoints I will later build to use different agents remotely. Cool.

- [x] Parse in txt or md file
- [x] Dynamically create API endpoint for agent (combination of system prompt and tools)
- [ ] Add method to parse input into InputText schema


## How to Use

### CLI

The CLI tool is located in `cli.py` and allows you to summarize or repurpose text files using the Summarizer Agent. It supports `.txt`, `.md`, and `.json` input files, as well as directories containing multiple files.

#### Basic Usage

Run the CLI with:

```bash
python summarizer-agent/cli.py summarize [--model-name MODEL] [--mcp-servers JSON] [--write-to-file True|False]
```

- `action` (required): Currently only `summarize` is supported.
- `--model-name`: (optional) The model to use (default: `openai:gpt-4o-mini`).
- `--mcp-servers`: (optional) JSON string for MCP server config. Example: `'{"transport": "http", "connection": "http://localhost:8000"}'`
- `--write-to-file`: (optional) If set to `True`, output will be saved as a markdown file in the `outputs/` directory. Otherwise, output is printed to the console.

#### Interactive Workflow

1. You will be prompted to enter the path to an input file or directory. Supported formats:
   - `.txt`: Plain text
   - `.md`: Markdown
   - `.json`: List of InputText objects (see `example_inputs/example_input.json`)
   - Directory: All supported files inside will be processed
2. Enter your prompt describing what you want the agent to do (e.g., "Summarize these articles as a newsletter").
3. The agent will process the input and display or save the output.
4. Type `exit` to quit the CLI.

#### Example Commands

- Summarize a single file and print output:
  ```bash
  python summarizer-agent/cli.py summarize --model-name openai:gpt-4o-mini
  # Then follow the prompts, e.g.:
  # Enter the path to the input file or directory of files: example_inputs/example_input.txt
  # What would you like me to do? Summarize this text in 3 bullet points.
  ```

- Summarize all `.txt` files in a directory and save output:
  ```bash
  python summarizer-agent/cli.py summarize --write-to-file True
  # Enter: example_inputs/inputs_txt
  # Enter your prompt as above
  ```

- Use a JSON input file:
  ```bash
  python summarizer-agent/cli.py summarize
  # Enter: example_inputs/example_input.json
  # Enter your prompt
  ```

- Use an MCP server (advanced):
  ```bash
  python summarizer-agent/cli.py summarize --mcp-servers '{"transport": "http", "connection": "http://localhost:8000"}'
  ```

#### Example Input Files
- `example_inputs/example_input.txt` (plain text)
- `example_inputs/example_input.json` (single/multi InputText objects)
- `example_inputs/inputs_txt/` (directory of .txt files)

The output will be saved in the `outputs/` directory if `--write-to-file True` is set.


