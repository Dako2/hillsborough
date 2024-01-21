# -*- coding: utf-8 -*-
import openai
import os 
from dotenv import load_dotenv
load_dotenv()

class Conversation:
    def __init__(self, system_prompt):
        
        self.client = openai.OpenAI(api_key = os.getenv("OPENAI_API_KEY"),) 
        self.messages = [
            {'role': 'system', 'content': system_prompt},
            ]

    def example(self):

        client = openai.OpenAI(api_key = os.environ.get("OPENAI_API_KEY")) 
        completion = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a poetic assistant, skilled in explaining complex programming concepts with creative flair."},
            {"role": "user", "content": "Compose a poem that explains the concept of recursion in programming."}
        ]
        )

        print(completion.choices[0].message)

        # Example usage
    def call_api(self, messages):
        try:
            #print(f"\n[userid: To ChatGPT] {messages}")
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo-1106",
                messages=messages,
                max_tokens=500,
                temperature=0.2
            )
            print(response.choices[0].message.content)
            return response.choices[0].message.content
        except Exception as e:
            print(f"Error during API call: {e}")
            return ""

    def rolling_convo(self, user_input, found_db_texts):
        self.messages.append({"role": "user", "content": user_input})

        if found_db_texts:
            found_db_texts_encoded = found_db_texts.replace('\u2019','')
            self.messages.append({"role": "system", "content": found_db_texts_encoded})

        chat_response = self.call_api(self.messages)

        # Remove the last system message if it was added
        if self.messages[-1]["role"] == "system":
            self.messages.pop()

        self.messages.append({"role": "assistant", "content": chat_response})

        return chat_response


if __name__ == "__main__":
    convo = Conversation('be a helpful assistant')
    user_input = "What are the benefits of ginger tea?"
    found_db_texts = "Some interesting facts about ginger tea..."
    #response = convo.rolling_convo(user_input, '')
    #print(response)

    #convo.example()

    messages = [{'role': 'system', 'content': 'be a traditional Chinese medicine doctor'}, {'role': 'user', 'content': 'What are the benefits of ginger tea?'}]
    convo.call_api(messages)

