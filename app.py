import os
from flask import Flask, request, jsonify, render_template, session
from werkzeug.utils import secure_filename
import openai
from langchain.document_loaders import PyPDFLoader, TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import FAISS
from langchain.chat_models import ChatOpenAI
from langchain.chains import ConversationalRetrievalChain
from langchain.memory import ConversationBufferMemory
import tempfile
import uuid
import json
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "default-secret-key")

# Configure upload folder
UPLOAD_FOLDER = 'uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Configure allowed extensions
ALLOWED_EXTENSIONS = {'pdf', 'txt'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def get_session_id():
    if 'session_id' not in session:
        session['session_id'] = str(uuid.uuid4())
    return session['session_id']

def get_vector_store_path(session_id):
    vector_stores_dir = 'vector_stores'
    if not os.path.exists(vector_stores_dir):
        os.makedirs(vector_stores_dir)
    return os.path.join(vector_stores_dir, f"{session_id}.faiss")

def get_chat_history_path(session_id):
    chat_history_dir = 'chat_history'
    if not os.path.exists(chat_history_dir):
        os.makedirs(chat_history_dir)
    return os.path.join(chat_history_dir, f"{session_id}.json")

def save_chat_history(session_id, history):
    path = get_chat_history_path(session_id)
    with open(path, 'w') as f:
        json.dump(history, f)

def load_chat_history(session_id):
    path = get_chat_history_path(session_id)
    if os.path.exists(path):
        with open(path, 'r') as f:
            return json.load(f)
    return []

def process_documents(files, api_key):
    documents = []
    temp_dir = tempfile.TemporaryDirectory()
    
    for file in files:
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file_path = os.path.join(temp_dir.name, filename)
            file.save(file_path)
            
            if filename.endswith('.pdf'):
                loader = PyPDFLoader(file_path)
                documents.extend(loader.load())
            elif filename.endswith('.txt'):
                loader = TextLoader(file_path)
                documents.extend(loader.load())
    
    # Split documents into chunks
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200
    )
    document_chunks = text_splitter.split_documents(documents)
    
    # Create embeddings and store in vector database
    openai.api_key = api_key
    embeddings = OpenAIEmbeddings(openai_api_key=api_key)
    
    session_id = get_session_id()
    vector_store_path = get_vector_store_path(session_id)
    
    vectorstore = FAISS.from_documents(document_chunks, embeddings)
    vectorstore.save_local(vector_store_path)
    
    return True

def get_conversation_chain(api_key):
    session_id = get_session_id()
    vector_store_path = get_vector_store_path(session_id)
    
    if not os.path.exists(vector_store_path):
        return None
    
    openai.api_key = api_key
    embeddings = OpenAIEmbeddings(openai_api_key=api_key)
    vectorstore = FAISS.load_local(vector_store_path, embeddings)
    
    llm = ChatOpenAI(
        model_name="gpt-3.5-turbo", 
        temperature=0,
        openai_api_key=api_key
    )
    
    memory = ConversationBufferMemory(
        memory_key="chat_history", 
        return_messages=True
    )
    
    conversation_chain = ConversationalRetrievalChain.from_llm(
        llm=llm,
        retriever=vectorstore.as_retriever(),
        memory=memory
    )
    
    return conversation_chain

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'files[]' not in request.files:
        return jsonify({'error': 'No files part'}), 400
    
    files = request.files.getlist('files[]')
    api_key = request.form.get('api_key')
    
    if not api_key:
        return jsonify({'error': 'API key is required'}), 400
    
    if not files or files[0].filename == '':
        return jsonify({'error': 'No files selected'}), 400
    
    try:
        process_documents(files, api_key)
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/chat', methods=['POST'])
def chat():
    data = request.json
    question = data.get('question')
    api_key = data.get('api_key')
    
    if not question:
        return jsonify({'error': 'Question is required'}), 400
    
    if not api_key:
        return jsonify({'error': 'API key is required'}), 400
    
    conversation_chain = get_conversation_chain(api_key)
    
    if not conversation_chain:
        return jsonify({'error': 'No documents processed yet'}), 400
    
    try:
        response = conversation_chain({'question': question})
        answer = response['answer']
        
        # Save chat history
        session_id = get_session_id()
        history = load_chat_history(session_id)
        history.append({'role': 'user', 'content': question})
        history.append({'role': 'assistant', 'content': answer})
        save_chat_history(session_id)
        
        return jsonify({'answer': answer})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/history', methods=['GET'])
def get_history():
    session_id = get_session_id()
    history = load_chat_history(session_id)
    return jsonify({'history': history})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
