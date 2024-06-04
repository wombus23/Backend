import os
from openai import OpenAI
from langchain.prompts import PromptTemplate
from langchain.chat_models import ChatOpenAI
from langchain.memory import ConversationBufferWindowMemory
from langchain.chains import ConversationalRetrievalChain
from langchain.embeddings import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS

def set_up_openai_key():
    """Sets up the OpenAI API key from environment variables."""
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("Please set the OPENAI_API_KEY environment variable.")
        exit()
    print(f"OpenAI API Key Retrieved: {api_key[:4]}...")  # Debugging line
    return OpenAI(api_key=api_key)

def create_custom_prompt_template():
    """Defines the custom prompt template for LLM guidance."""
    custom_template = """<s>[INST]You will start the conversation by greeting the user and introducing yourself as qanoon-bot,
    stating your availability for legal assistance in Pakistan. Your next step will depend on the user's response.
    If the user expresses a need for legal assistance, you will ask them to describe their case or problem.
    Based on the user given preference you have to respond in the required language by the user (English or Urdu only).
    After receiving the case or problem details from the user, you will provide the solutions and procedures according to the knowledge base and also give related penal codes and procedures.
    However, if the user does not require legal assistance in Pakistan, you will immediately thank them and
    say goodbye, ending the conversation. Remember to base your responses on the user's needs, providing accurate and
    concise information regarding the Pakistan legal law and rights where applicable. Your interactions should be professional and
    focused, ensuring the user's queries are addressed efficiently without deviating from the set flows.
    CONTEXT: {context}
    CHAT HISTORY: {chat_history}
    QUESTION: {question}
    ANSWER:
    </s>[INST]
    """
    return custom_template

def initialize_embeddings(optional=True):
    """Initializes embeddings for text (optional, for vector store)."""
    if optional:
        embeddings = OpenAIEmbeddings()
        return embeddings
    else:
        print("Embeddings initialization skipped (optional).")
        return None

def load_vector_database(embeddings, optional=True):
    """Loads a pre-built vector database (optional)."""
    if optional:
        # Replace with your vector database loading code (e.g., FAISS)
        db = FAISS.load_local("vectordb", embeddings, allow_dangerous_deserialization=True)
        db_retriever = db.as_retriever(search_type="similarity", search_kwargs={"k": 4})
        return db_retriever
    else:
        print("Vector database loading skipped (optional).")
        return None

def create_conversation_memory():
    """Initializes conversation memory for context."""
    memory = ConversationBufferWindowMemory(k=5, memory_key="chat_history", return_messages=True, output_key='answer')
    return memory

def initialize_prompt(prompt_template, memory):
    """Combines the prompt template with memory retrieval."""
    prompt = PromptTemplate(template=prompt_template, input_variables=['context', 'chat_history', 'question'])
    return prompt

def initialize_llm(model_name='gpt-3.5-turbo-0125', temperature=0.2):
    """Initializes the LLM model (ChatGPT)."""
    llm = ChatOpenAI(temperature=temperature, model_name=model_name)
    return llm

def create_conversational_retrieval_chain(llm, memory, retriever=None):
    """Combines retrieval (optional) and LLM for conversation flow."""
    qa = ConversationalRetrievalChain.from_llm(
        llm=llm,
        memory=memory,
        retriever=retriever  # Use the retriever if loaded
    )
    return qa

def process_conversation(qa, input_prompt, messages):
    """Processes a conversation turn with the LLM."""
    # Add user input to messages
    messages.append({"role": "user", "content": input_prompt})

    # Invoke the ConversationalRetrievalChain with the user input
    result = qa.invoke(input=input_prompt)

    # Get the assistant's response and add it to messages
    assistant_response = result["answer"]
    messages.append({"role": "assistant", "content": assistant_response})
    return assistant_response
