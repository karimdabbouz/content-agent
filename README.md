# Writer Agent

The goal is to build an LLM agent that can accept one or n number of input texts and then flexibly rewrite them into a given format, i.e. a blog post, an article, a newsletter etc.

I want this to be as flexible and modular as possible in order to be able to integrate it into different workflows. I am therefore building the agent as an MCP client using PydanticAI that can connect to MCP servers either for receiving input and/or for sending output. Example workflow: Receive a number of weekly newsletters, repurpose them into a single article and create a draft in Wordpress. Or receive a number of newsletters and summarize them into a single one which is then sent to my mail address using a Gmail MCP server (who reads all those newsletters anyway?)

An agent can be seen as a combination of MCP servers for input and/or output and a system prompt. Hence, agents will be created at startup of the webserver and can then be used through their respective endpoints. They will live in memory and can be altered at runtime through the API. This should work for a small number of agents (running MCP servers is another story, but they will most likely be used by multiple agents anyway). Actions in the CLI app correspond to API endpoints I will later build to use different agents remotely. Cool.

## How to Use

### CLI

The CLI tool is located in `cli.py` and allows you to work with text from files or web searches using the Writer Agent. It supports `.txt`, `.md`, and `.json` input files, as well as directories containing multiple files.

#### Basic Usage

Run the CLI with:

```bash
python content-agent/cli.py [action] [--model-name MODEL] [--mcp-servers JSON] [--write-to-file True|False]
```

- `action` (required): Choose between `from-file` or `from-web`
- `--model-name`: (optional) The model to use (default: `openai:gpt-4o-mini`)
- `--mcp-servers`: (optional) JSON string for MCP server config. Can be a single config or an array of configs:
  ```bash
  # Single server
  --mcp-servers '{"transport": "http", "connection": "http://localhost:8000"}'
  
  # Multiple servers
  --mcp-servers '[{"transport": "http", "connection": "http://localhost:8000"}, {"transport": "stdio", "connection": ["/usr/bin/firecrawl", ["--arg1", "foo"]]}]'
  ```
- `--write-to-file`: (optional) If set to `True`, output will be saved as a markdown file in the `outputs/` directory. Otherwise, output is printed to the console.

#### Actions

##### from-file
Work with text from one or more files:
```bash
python content-agent/cli.py from-file --file-path PATH [--model-name MODEL] [--mcp-servers JSON] [--write-to-file True|False]
```
- `--file-path`: (required) Path to the input file or directory. Supported formats:
  - `.txt`: Plain text
  - `.md`: Markdown
  - `.json`: List of InputText objects (see `example_inputs/example_input.json`)
  - Directory: All supported files inside will be processed

##### from-file-with-outline
Work with text from one or more files, create an outline first, then generate content from the outline:
```bash
python content-agent/cli.py from-file-with-outline --file-path PATH [--model-name MODEL] [--mcp-servers JSON] [--write-to-file True|False]
```
- `--file-path`: (required) Path to the input file or directory.

##### create-outline-only
Create an outline from input texts without writing the actual content:
```bash
python content-agent/cli.py create-outline-only --file-path PATH [--model-name MODEL] [--mcp-servers JSON] [--write-to-file True|False]
```
- `--file-path`: (required) Path to the input file or directory.

##### from-web
Work with text gathered from a web search (requires Firecrawl MCP server):
```bash
python content-agent/cli.py from-web --mcp-servers '{"transport": "sse", "connection": "https://mcp.firecrawl.dev/{FIRECRAWL_API_KEY}/sse"}' [--model-name MODEL] [--write-to-file True|False]
```
- Replace `{FIRECRAWL_API_KEY}` with your actual Firecrawl API key.
- This gives the agent access to the web via Firecrawl using SSE transport.

Example:
```bash
python content-agent/cli.py from-web --mcp-servers '{"transport": "sse", "connection": "https://mcp.firecrawl.dev/abc123/sse"}'
```

#### Interactive Workflow

1. After starting the CLI with the appropriate action and arguments, you'll be prompted to enter your instructions (and, for from-file-with-outline, to first create an outline, then generate content).
2. The agent will process your request and display or save the output.
3. Type `exit` to quit the CLI.

#### Example Commands

- Work with a single file:
  ```bash
  python content-agent/cli.py from-file --file-path example_inputs/example_input.txt
  # Then enter your prompt, e.g.:
  # What would you like me to do? Summarize this text in 3 bullet points.
  ```

- Work with all files in a directory and save output:
  ```bash
  python content-agent/cli.py from-file --file-path example_inputs/inputs_txt --write-to-file True
  ```

- Use with an MCP server:
  ```bash
  python content-agent/cli.py from-file --file-path example_inputs/example_input.txt --mcp-servers '{"transport": "http", "connection": "http://localhost:8000"}'
  ```

- Create an outline only:
  ```bash
  python content-agent/cli.py create-outline-only --file-path example_inputs/example_input.txt
  ```

- Create an outline and then generate content from it:
  ```bash
  python content-agent/cli.py from-file-with-outline --file-path example_inputs/example_input.txt
  ```

#### Example Input Files
- `example_inputs/example_input.txt` (plain text)
- `example_inputs/example_input.json` (single/multi InputText objects)
- `example_inputs/inputs_txt/` (directory of .txt files)

The output will be saved in the `outputs/` directory if `--write-to-file True` is set.


