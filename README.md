Snap & Study – AI Learning Assistant

Project Overview

Snap & Study is an AI-powered learning assistant designed to help students understand academic topics, generate study summaries, and revise concepts efficiently.

The application uses Google's Gemini AI model to provide explanations and learning support through a simple, interactive interface built with Streamlit.

Features

- AI Topic Explanation: Understand academic concepts in simple language.
- Image-Based Learning: Upload an image containing academic content for AI assistance.
- AI Study Summaries: Generate organized notes for revision.
- Interactive AI Chatbot: Ask follow-up questions and clarify doubts.
- Download Notes: Save generated study material.
- Email Sharing: Share learning content through email.
- WhatsApp Sharing: Share notes using WhatsApp.
- Telegram Integration: Send learning content through a Telegram bot.

Technologies Used

- Python
- Streamlit
- Google Gemini API
- Google Gen AI SDK
- Pillow
- Requests
- Resend API
- Telegram Bot API

Project Structure

Snap & Study/
│
├── app.py
├── prompts.py
├── requirements.txt
├── .gitignore
├── README.md
└── .streamlit/
    └── secrets.toml

Note: The "secrets.toml" file contains private API credentials and must not be uploaded to GitHub.

Installation and Setup

1. Clone the repository

git clone YOUR_GITHUB_REPOSITORY_URL

2. Open the project folder

cd "Snap & Study"

3. Install dependencies

pip install -r requirements.txt

4. Configure API credentials

Create a ".streamlit/secrets.toml" file and configure the required credentials:

- "GEMINI_API_KEY"
- "RESEND_API_KEY"
- "TELEGRAM_BOT_TOKEN"

Never publish actual API keys or tokens.

5. Run the application

python -m streamlit run app.py

Purpose

The purpose of Snap & Study is to make learning more accessible, interactive, and convenient by combining AI-based explanations, summaries, and content-sharing features in one application.

Developer

Developed as an AI-powered educational project for student learning.