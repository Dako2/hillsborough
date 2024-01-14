import openai

system_content = "You are a traidtional Chinese medicine doctor. you analyze the patient's symptoms and recommend a treatement and a herbal tea"
user_content = "最近我老是贪睡得病感冒，有什么茶推荐吗？"

client = openai.OpenAI(
    api_key="2dd676e4528ce88cd7e66bd036e2d74d98d51ed4f4c3f5463e885d33e88fb5ba",
    base_url="https://api.together.xyz/v1",
    )

stream = client.chat.completions.create(
    model="willwuwork@gmail.com/Mistral-7B-Instruct-v0.2-2024-01-13-23-14-34",
    messages=[
        {"role": "system", "content": system_content},
        {"role": "user", "content": user_content},
    ],
    stream=True,
    max_tokens=1024,
    stop=['</s>']
)
for chunk in stream:
    print(chunk.choices[0].delta.content or "", end="", flush=True)