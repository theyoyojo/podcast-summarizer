#!/usr/bin/env python3

import argparse
import openai
import os

parser = argparse.ArgumentParser(prog='summarize')

parser.add_argument('-q',
                    '--query',
                    type=str,
                    required=True,
                    help='chatgpt query')


# Set your API key from an environment variable for security
# The OpenAI library will automatically pick this up.
# On macOS/Linux, you would run: export OPENAI_API_KEY='your-api-key'
# On Windows, you would run: set OPENAI_API_KEY='your-api-key'

client = openai.OpenAI()

def main():
    args = parser.parse_args()
    print(f'ChatGPT: {chatgpt(args.query)}')

def chatgpt(query):
    messages=[]
    # if json:
    #    messages += [{"role": "system", "content": "Output valid JSON"},]
    messages +=[{"role": "user", "content": query }]


    try:
        # Make the API call to the chat completions endpoint
        response = client.chat.completions.create(
            model="gpt-4o",  # Specify the model you want to use
            messages=messages,
        )

        # Extract the assistant's message from the response
        # The response is an object, and the message is in the first choice.
        return response.choices[0].message.content

    except openai.APIError as e:
        print(f'An API error occurred: {e}')
    except Exception as e:
        print('"An unexpected error occurred: {e}')

if __name__ == '__main__':
    main()
