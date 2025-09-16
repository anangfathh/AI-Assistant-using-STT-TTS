This project is a web-based, voice-enabled chatbot powered by Google's Gemini API and built with a FastAPI backend and a simple HTML/CSS/JavaScript frontend.

Features
Interactive Chat Interface: A clean and modern chat window to display the conversation.

Text Input: Send messages to the Gemini model by typing.

Voice Input: Record audio directly in the browser to have a spoken conversation.

Speech-to-Text: Transcribes user's voice into text for processing by the AI.

Text-to-Speech: Converts the AI's text response back into audible speech for a natural interaction.

Real-time Feedback: UI indicators show when the application is busy processing a request.

Project Structure
.
├── static/
│ └── audio/ # Directory to store generated TTS audio files
├── .env # For storing your API key securely
├── main.py # The FastAPI backend server application
├── index.html # The HTML file for the frontend user interface
├── requirements.txt # A list of all required Python packages
└── README.md # This setup and information file

Prerequisites
Before you begin, ensure you have the following installed on your system:

Python: Version 3.9 or newer.

pip: Python's package installer (usually comes with Python).

ffmpeg: A crucial, external dependency for handling audio conversion.

Windows: Download from ffmpeg.org and add the bin folder to your system's PATH.

macOS: Install using Homebrew with brew install ffmpeg.

Debian/Ubuntu: Install using apt with sudo apt-get install ffmpeg.

Setup Instructions
Follow these steps to get the application running on your local machine.

1. Clone the Repository
   First, get the source code onto your machine. If you're using git, you can clone the repository. Otherwise, simply download and unzip the project files.

2. Create a Virtual Environment
   It's highly recommended to use a virtual environment to keep project dependencies isolated.

# Navigate into your project directory

cd path/to/your/project

# Create a virtual environment

python -m venv venv

# Activate the virtual environment

# On Windows:

venv\Scripts\activate

# On macOS/Linux:

source venv/bin/activate

3. Install Dependencies
   Install all the required Python packages using the requirements.txt file. Note: This now includes python-dotenv to handle the .env file.

pip install -r requirements.txt

4. Set Up Your API Key in a .env File
   The application loads your Google Gemini API key from a .env file for security.

Obtain your key from Google AI Studio.

In the root of your project directory, create a new file named .env.

Add the following line to the .env file, replacing YOUR_API_KEY_HERE with your actual key:

GEMINI_API_KEY="YOUR_API_KEY_HERE"

5. Run the Application
   Start the FastAPI server using uvicorn. The script will automatically find and load your API key from the .env file.

uvicorn main:app --reload

The --reload flag is for development and will automatically restart the server when you make code changes.

6. Access the Chatbot
   Open your web browser and navigate to the following address:

http://127.0.0.1:8000

You should now see the chat interface and can begin interacting with your AI assistant.
