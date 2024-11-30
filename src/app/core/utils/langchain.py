import os
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
from langchain_core.prompts import ChatPromptTemplate

load_dotenv()

openai_key = os.getenv("OPENAI_API_KEY")
# Set up the LLM
llm = ChatOpenAI(
    model="gpt-4o",
    temperature=0,
    max_tokens=None,
    timeout=None,
    max_retries=2,
)
system_message = (
    "You are a helpful assistant capable of generating code for RESTful and GraphQL APIs based on user requests. "
    "Continue the conversation by answering or asking for more details. "
    "You will exit only if the user types 'exit'."
)
prompt = ChatPromptTemplate.from_messages(
    [
        ("system", system_message),
        ("human", "{input}"),
    ]
)
conversation_history = []
# Chat loop
def chat():
    print(
        "Welcome! You can ask me to generate code for RESTful or GraphQL APIs. Type 'exit' to quit."
    )
    while True:
        user_input = input("You: ").strip()
        if user_input.lower() == "exit":
            print("Exiting... Goodbye!")
            break
        conversation_history.append(("human", user_input))
        messages = [(system_message,)] + conversation_history
        chain = prompt | llm
        response = chain.invoke({"input": user_input})
        conversation_history.append(("assistant", response.content))
        print(f"Bot: {response.content}")
