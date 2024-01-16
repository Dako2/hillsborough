import openai
import os

def chat_with_gpt(prompt, model="text-davinci-003", temperature=0.7):
    """
    Function to chat with GPT.
    :param prompt: The message to send to GPT.
    :param model: The model to use. Default is 'text-davinci-003'.
    :param temperature: The temperature to use for the response. Default is 0.7.
    :return: The response from GPT.
    """
    openai.api_key = os.getenv('OPENAI_API_KEY')  # Get API key from environment variable

    response = openai.ChatCompletion.create(
        model=model,
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt}
        ],
        temperature=temperature
    )

    return response.choices[0].message['content']

# Example usage
user_input = "Hello, how are you?"
response = chat_with_gpt(user_input)
print(response)
