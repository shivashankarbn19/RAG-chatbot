import os
import sys

# Create necessary directories
directories = ['uploads', 'vector_stores', 'chat_history', 'templates']
for directory in directories:
    if not os.path.exists(directory):
        os.makedirs(directory)
        print(f"Created directory: {directory}")

# Check if templates/index.html exists
if not os.path.exists('templates/index.html'):
    print("Error: templates/index.html not found")
    sys.exit(1)

print("Build completed successfully")
