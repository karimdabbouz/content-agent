import logfire, os
from dotenv import load_dotenv


load_dotenv()

LOGFIRE_TOKEN = os.getenv("LOGFIRE_TOKEN")

logfire.configure(token=LOGFIRE_TOKEN)

def main():
    logfire.info('Hello, {place}!', place='World')


if __name__ == '__main__':
    main()