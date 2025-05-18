import streamlit as st
import os
import tempfile
from langchain.document_loaders import PyPDFLoader, TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import FAISS
from langchain.chat_models import ChatOpenAI
from langchain.chains import ConversationalRetrievalChain
from langchain.memory import ConversationBufferMemory

# Page configuration
st.set_page_config(page_title="RAG Chatbot", page_icon="🤖")
st.title("RAG Chatbot")

# Initialize session state variables
if "conversation" not in st.session_state:
    st.session_state.conversation = None
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "processComplete" not in st.session_state:
    st.session_state.processComplete = False

# Function to process uploaded documents
def process_documents(uploaded_files):
    documents = []
    temp_dir = tempfile.TemporaryDirectory()
    for file in uploaded_files:
        temp_file_path = os.path.join(temp_dir.name, file.name)
        with open(temp_file_path, "wb") as f:
            f.write(file.getvalue())
        
        if file.name.endswith(".pdf"):
            loader = PyPDFLoader(temp_file_path)
            documents.extend(loader.load())
        elif file.name.endswith(".txt"):
            loader = TextLoader(temp_file_path)
            documents.extend(loader.load())
    
    # Split documents into chunks
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200
    )
    document_chunks = text_splitter.split_documents(documents)
    
    # Create embeddings and store in vector database
    embeddings = OpenAIEmbeddings()
    vectorstore = FAISS.from_documents(document_chunks, embeddings)
    
    # Create conversation chain
    llm = ChatOpenAI(model_name="gpt-3.5-turbo", temperature=0)
    memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)
    conversation_chain = ConversationalRetrievalChain.from_llm(
        llm=llm,
        retriever=vectorstore.as_retriever(),
        memory=memory
    )
    
    return conversation_chain

# Sidebar for API key and document upload
with st.sidebar:
    st.header("Configuration")
    api_key = st.text_input("Enter your OpenAI API key:", type="password")
    if api_key:
        os.environ["OPENAI_API_KEY"] = api_key
    
    uploaded_files = st.file_uploader("Upload documents to your knowledge base:", accept_multiple_files=True)
    if uploaded_files and api_key and st.button("Process Documents"):
        with st.spinner("Processing documents..."):
            st.session_state.conversation = process_documents(uploaded_files)
            st.session_state.processComplete = True
            st.success("Documents processed successfully!")

# Main chat interface
if st.session_state.processComplete:
    user_question = st.chat_input("Ask a question about your documents:")
    if user_question:
        st.session_state.chat_history.append({"role": "user", "content": user_question})
        
        with st.spinner("Thinking..."):
            response = st.session_state.conversation({"question": user_question})
            st.session_state.chat_history.append({"role": "assistant", "content": response["answer"]})

    # Display chat history
    for message in st.session_state.chat_history:
        with st.chat_message(message["role"]):
            st.write(message["content"])
else:
    st.info("Please upload documents and process them to start chatting.")

# Add information about the app
with st.expander("About this app"):
    st.markdown("""
    This chatbot uses Retrieval Augmented Generation (RAG) to provide accurate answers based on your documents.
    
    1. Upload PDF or TXT files to create your knowledge base
    2. Ask questions related to the content of your documents
    3. The chatbot will retrieve relevant information and generate accurate responses
    
    Built with Streamlit, LangChain, and OpenAI.
    """)
