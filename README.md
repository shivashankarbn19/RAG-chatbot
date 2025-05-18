# RAG Chatbot with Streamlit

This is a Retrieval Augmented Generation (RAG) chatbot built with Streamlit, LangChain, and OpenAI. The chatbot allows users to upload documents (PDF, TXT) and ask questions about their content.

## Features

- Upload PDF and TXT files to create a knowledge base
- Ask questions about the uploaded documents
- Get accurate answers based on the document content
- Conversation history tracking

## Requirements

- Python 3.8+
- OpenAI API key

## Installation

1. Clone this repository
2. Install the required packages:
   \`\`\`
   pip install -r requirements.txt
   \`\`\`
3. Run the app locally:
   \`\`\`
   streamlit run app.py
   \`\`\`

## Deployment on Streamlit Cloud

1. Fork this repository to your GitHub account
2. Go to [Streamlit Cloud](https://streamlit.io/cloud)
3. Sign in with your GitHub account
4. Click "New app"
5. Select this repository and the main file (app.py)
6. Deploy the app

## Usage

1. Enter your OpenAI API key in the sidebar
2. Upload one or more documents (PDF or TXT)
3. Click "Process Documents"
4. Start asking questions about your documents

## How it Works

This chatbot uses Retrieval Augmented Generation (RAG):

1. Documents are split into chunks
2. Chunks are embedded using OpenAI embeddings
3. Embeddings are stored in a FAISS vector database
4. When a question is asked, the most relevant chunks are retrieved
5. The LLM generates an answer based on the retrieved information
\`\`\`

Let's also create a .gitignore file:

```txt file=".gitignore" type="code"
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
env/
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
*.egg-info/
.installed.cfg
*.egg

# Virtual Environment
venv/
ENV/
env/

# Streamlit
.streamlit/

# IDE
.idea/
.vscode/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db
