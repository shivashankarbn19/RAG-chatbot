from setuptools import setup, find_packages

setup(
    name="rag-chatbot",
    version="0.1",
    packages=find_packages(),
    install_requires=[
        "streamlit",
        "langchain",
        "openai",
        "faiss-cpu",
        "pypdf",
        "python-dotenv",
    ],
)
