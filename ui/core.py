from openai import OpenAI
import json
import time

def show_json(obj):
    print(json.loads(obj.model_dump_json()))

TCM_ASSISTANT_ID = 'asst_FjBZXd9Zjgocx710JqH0Q6Kr'
client = OpenAI()
 
assistant = client.beta.assistants.update(
    TCM_ASSISTANT_ID,
    tools=[{"type": "retrieval"}],
    )
show_json(assistant)

# Pretty printing helper
def pretty_print(messages):
    print("# Messages")
    for m in messages:
        print(f"{m.role}: {m.content[0].text.value}")
    print()

def wait_on_run(run, thread):
    while run.status == "queued" or run.status == "in_progress":
        run = client.beta.threads.runs.retrieve(
            thread_id=thread.id,
            run_id=run.id,
        )
        time.sleep(0.5)
    return run

def submit_message(assistant_id, thread, user_message):
    client.beta.threads.messages.create(
        thread_id=thread.id, role="user", content=user_message
    )
    return client.beta.threads.runs.create(
        thread_id=thread.id,
        assistant_id=assistant_id,
    )

def get_response(thread):
    return client.beta.threads.messages.list(thread_id=thread.id, order="asc")

def create_thread_and_run(user_input):
    thread = client.beta.threads.create()
    run = submit_message(TCM_ASSISTANT_ID, thread, user_input)
    return thread, run

def recommend(symptom):
    thread, run = create_thread_and_run(
        symptom
    )
    run = wait_on_run(run, thread)
    messages = get_response(thread)
    pretty_print(messages)

    for m in messages:
        print(f"{m.role}: {m.content[0].text.value}")

    return messages
