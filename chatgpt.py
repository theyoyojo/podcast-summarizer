#!/usr/bin/env python3

import openai
import argparse

# Set your API key from an environment variable for security
# The OpenAI library will automatically pick this up.
# On macOS/Linux, you would run: export OPENAI_API_KEY='your-api-key'
# On Windows, you would run: set OPENAI_API_KEY='your-api-key'


def chatgpt(query):
    client = openai.OpenAI()
    messages = []
    messages += [{"role": "user", "content": query}]

    try:
        response = client.chat.completions.create(
            model="gpt-4o",  # Specify the model you want to use
            messages=messages,
        )

        return response.choices[0].message.content

    except openai.APIError as e:
        print(f'An API error occurred: {e}')
    except Exception as e:
        print(f'An unexpected error occurred: {e}')


parser = argparse.ArgumentParser(prog='chatgpt')

parser.add_argument('-q',
                    '--query',
                    type=str,
                    required=True,
                    help='chatgpt query')


def main():
    args = parser.parse_args()
    print(f'ChatGPT: {chatgpt(args.query)}')


if __name__ == '__main__':
    main()
