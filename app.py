import streamlit as st
import requests
import resend
import re

from urllib.parse import quote
from google import genai
from PIL import Image


# ==================================================
# PAGE CONFIGURATION
# ==================================================

st.set_page_config(
    page_title="Snap & Study",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="collapsed"
)


# ==================================================
# CUSTOM CSS
# ==================================================

st.markdown("""
<style>

.stApp {
    background: linear-gradient(
        135deg,
        #101827,
        #192b43,
        #101827
    );
    color: #ffffff;
}

[data-testid="stHeader"] {
    background: transparent;
}

.block-container {
    max-width: 1100px;
    padding-top: 2rem;
    padding-bottom: 3rem;
}

h1, h2, h3 {
    color: #ffffff !important;
}

p, label, .stMarkdown {
    color: #e2e8f0;
}

.stButton > button {
    background: linear-gradient(
        90deg,
        #7657f6,
        #a855f7
    );
    color: white;
    border: none;
    border-radius: 12px;
    min-height: 48px;
    font-weight: 700;
    transition: 0.2s;
}

.stButton > button:hover {
    background: linear-gradient(
        90deg,
        #6242e8,
        #9333ea
    );
    color: white;
    border: none;
    transform: translateY(-2px);
}

.stDownloadButton > button,
.stLinkButton > a {
    background: #263c58;
    color: white;
    border: 1px solid #526985;
    border-radius: 10px;
}

[data-testid="stTextArea"] textarea,
[data-testid="stTextInput"] input {
    background: #1e3049;
    color: white;
    border-radius: 10px;
}

[data-testid="stFileUploader"] {
    background: #1e3049;
    border: 1px dashed #64748b;
    border-radius: 14px;
    padding: 15px;
}

[data-testid="stVerticalBlockBorderWrapper"] {
    background: #1c2c43;
    border-radius: 16px;
    border-color: #344b68;
}

hr {
    border-color: #405570;
}

</style>
""", unsafe_allow_html=True)


# ==================================================
# SESSION STATE
# ==================================================

if "started" not in st.session_state:
    st.session_state.started = False

if "ai_explanation" not in st.session_state:
    st.session_state.ai_explanation = ""

if "study_summary" not in st.session_state:
    st.session_state.study_summary = ""

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

if "original_question" not in st.session_state:
    st.session_state.original_question = ""

if "learning_level" not in st.session_state:
    st.session_state.learning_level = "Beginner"


# ==================================================
# WELCOME PAGE
# ==================================================

if not st.session_state.started:

    st.write("")
    st.write("")

    st.markdown(
        "<h1 style='text-align:center;"
        "font-size:44px;'>"
        "📚 Welcome to Snap & Study! ✨"
        "</h1>",
        unsafe_allow_html=True
    )

    st.markdown(
        "<h3 style='text-align:center;"
        "color:#c4b5fd !important;'>"
        "Your Personal AI Learning Companion"
        "</h3>",
        unsafe_allow_html=True
    )

    st.write("")

    st.markdown(
        "<p style='text-align:center;"
        "font-size:18px;line-height:1.8;'>"
        "Upload a question, snap your notes, or enter "
        "any topic you want to understand.<br>"
        "Learn concepts in simple language, prepare for "
        "exams, and revise smarter with AI."
        "</p>",
        unsafe_allow_html=True
    )

    st.write("")
    st.write("")

    # FEATURE CARDS

    col1, col2, col3 = st.columns(3)

    with col1:
        with st.container(border=True):
            st.markdown(
                "<h1 style='text-align:center;'>📸</h1>",
                unsafe_allow_html=True
            )

            st.markdown(
                "<h3 style='text-align:center;'>"
                "Snap & Upload</h3>",
                unsafe_allow_html=True
            )

            st.markdown(
                "<p style='text-align:center;'>"
                "Upload questions, images, and study notes."
                "</p>",
                unsafe_allow_html=True
            )

    with col2:
        with st.container(border=True):
            st.markdown(
                "<h1 style='text-align:center;'>🤖</h1>",
                unsafe_allow_html=True
            )

            st.markdown(
                "<h3 style='text-align:center;'>"
                "AI Explanation</h3>",
                unsafe_allow_html=True
            )

            st.markdown(
                "<p style='text-align:center;'>"
                "Understand difficult concepts in simple words."
                "</p>",
                unsafe_allow_html=True
            )

    with col3:
        with st.container(border=True):
            st.markdown(
                "<h1 style='text-align:center;'>📝</h1>",
                unsafe_allow_html=True
            )

            st.markdown(
                "<h3 style='text-align:center;'>"
                "Smart Revision</h3>",
                unsafe_allow_html=True
            )

            st.markdown(
                "<p style='text-align:center;'>"
                "Create summaries and prepare for exams."
                "</p>",
                unsafe_allow_html=True
            )

    st.write("")
    st.write("")

    left, center, right = st.columns([1, 2, 1])

    with center:

        if st.button(
            "🚀 Start Learning",
            use_container_width=True
        ):
            st.session_state.started = True
            st.rerun()

    st.write("")
    st.write("")

    st.markdown(
        "<p style='text-align:center;color:#94a3b8;'>"
        "Learn smarter. Understand better. Grow every day. ❤️"
        "</p>",
        unsafe_allow_html=True
    )

    st.stop()


# ==================================================
# GEMINI CONFIGURATION
# ==================================================

try:
    api_key = st.secrets["GEMINI_API_KEY"]
    client = genai.Client(api_key=api_key)

except Exception as e:
    st.error(
        "Gemini API configuration error. "
        "Please check your secrets.toml file."
    )
    st.stop()


MODEL_NAME = "gemini-3.5-flash"


# ==================================================
# AI FUNCTION
# ==================================================

def generate_ai_response(prompt, image=None):

    try:
        contents = [prompt]

        if image is not None:
            contents.append(image)

        response = client.models.generate_content(
            model=MODEL_NAME,
            contents=contents
        )

        return response.text or "No response was generated."

    except Exception as e:
        return f"AI request failed: {str(e)}"


# ==================================================
# TELEGRAM CHUNK FUNCTION
# ==================================================

def split_telegram_content(content, limit=3500):

    chunks = []
    current = ""

    for line in content.splitlines():

        if len(current) + len(line) + 1 > limit:

            if current:
                chunks.append(current)

            current = line

        else:
            current += "\n" + line

    if current:
        chunks.append(current)

    return chunks


# ==================================================
# LEARNING DASHBOARD
# ==================================================

st.title("📚 Snap & Study")

st.caption(
    "Your AI-powered learning assistant"
)

if st.button("← Back to Welcome Page"):

    st.session_state.started = False
    st.rerun()

st.divider()

st.header("✨ Learn Something New")

st.write(
    "Upload a question or enter a topic "
    "to begin your learning journey."
)


# ==================================================
# INPUT SECTION
# ==================================================

uploaded_file = st.file_uploader(
    "📸 Upload your question or notes",
    type=["png", "jpg", "jpeg"]
)

if uploaded_file is not None:

    st.image(
        uploaded_file,
        caption="Uploaded study material",
        use_container_width=True
    )

question = st.text_area(
    "✍️ Enter your question or topic",
    placeholder=(
        "Example: Explain DFA in simple words..."
    ),
    height=120
)

learning_level = st.selectbox(
    "🎓 Select your learning level",
    [
        "Beginner",
        "Intermediate",
        "Advanced",
        "Exam Preparation"
    ]
)


# ==================================================
# GENERATE EXPLANATION
# ==================================================

if st.button(
    "✨ Generate AI Explanation",
    use_container_width=True
):

    if not question.strip() and uploaded_file is None:

        st.warning(
            "Please enter a question or upload an image."
        )

    else:

        prompt = f"""
You are Snap & Study, a friendly academic AI tutor.

Student learning level: {learning_level}

Student question:
{question if question.strip() else "Explain the uploaded image."}

Instructions:

1. Identify the main topic.
2. Explain the concept in simple language.
3. Explain important terminology.
4. Use step-by-step explanations when useful.
5. Include examples.
6. Include important formulas or technical facts.
7. Make the answer useful for exam preparation.
8. Do not invent information.
9. Mention if the uploaded image is unclear.

Use headings and bullet points.
"""

        image_data = None

        if uploaded_file is not None:
            image_data = Image.open(uploaded_file)

        with st.spinner(
            "🤖 Your AI tutor is preparing the explanation..."
        ):

            result = generate_ai_response(
                prompt,
                image_data
            )

        if result.startswith("AI request failed:"):

            st.error(result)

        else:

            st.session_state.ai_explanation = result
            st.session_state.original_question = question
            st.session_state.learning_level = learning_level
            st.session_state.study_summary = ""
            st.session_state.chat_history = []

            st.success("Explanation generated successfully!")


# ==================================================
# EXPLANATION
# ==================================================

if st.session_state.ai_explanation:

    st.divider()

    st.header("📖 AI Explanation")

    st.markdown(
        st.session_state.ai_explanation
    )


    # ==================================================
    # SUMMARY
    # ==================================================

    if st.button(
        "📝 Generate Study Summary",
        use_container_width=True
    ):

        summary_prompt = f"""
You are an expert academic summarization assistant.

Create a clear, accurate, student-friendly summary
from the following explanation.

{st.session_state.ai_explanation}

Use this structure:

# Topic

## Overview

## Key Concepts

## Important Definitions

## Important Formulas or Facts

## Key Takeaways

## Quick Revision

Use simple language.
Preserve relevant formulas and technical terms.
Do not introduce unsupported information.
"""

        with st.spinner("Creating your study summary..."):

            summary = generate_ai_response(
                summary_prompt
            )

        if summary.startswith("AI request failed:"):
            st.error(summary)

        else:
            st.session_state.study_summary = summary
            st.success("Study summary generated!")


    if st.session_state.study_summary:

        st.divider()

        st.header("📝 Study Summary")

        st.markdown(
            st.session_state.study_summary
        )


    # ==================================================
    # CHATBOT
    # ==================================================

    st.divider()

    st.header("💬 Ask Your AI Tutor")

    st.write(
        "Ask follow-up questions about your topic."
    )

    for message in st.session_state.chat_history:

        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    user_message = st.chat_input(
        "Ask a question about this topic..."
    )

    if user_message:

        st.session_state.chat_history.append({
            "role": "user",
            "content": user_message
        })

        with st.chat_message("user"):
            st.markdown(user_message)

        history = ""

        for message in st.session_state.chat_history[:-1]:

            role = (
                "Student"
                if message["role"] == "user"
                else "AI Tutor"
            )

            history += (
                f"{role}: {message['content']}\n"
            )

        chat_prompt = f"""
You are a friendly academic AI tutor.

Original question:
{st.session_state.original_question}

Learning level:
{st.session_state.learning_level}

Previous explanation:
{st.session_state.ai_explanation}

Study summary:
{st.session_state.study_summary}

Conversation:
{history}

New student question:
{user_message}

Explain clearly and simply.
Use examples when useful.
"""

        with st.chat_message("assistant"):

            with st.spinner("Thinking..."):

                answer = generate_ai_response(
                    chat_prompt
                )

            st.markdown(answer)

        st.session_state.chat_history.append({
            "role": "assistant",
            "content": answer
        })


    # ==================================================
    # SHARE CONTENT
    # ==================================================

    share_content = f"""
SNAP & STUDY
Your Personal AI Learning Notes

QUESTION / TOPIC:
{st.session_state.original_question}

AI EXPLANATION:
{st.session_state.ai_explanation}

STUDY SUMMARY:
{st.session_state.study_summary or "No summary generated."}

CHAT HISTORY:
"""

    for message in st.session_state.chat_history:

        role = (
            "Student"
            if message["role"] == "user"
            else "AI Tutor"
        )

        share_content += (
            f"\n{role}: {message['content']}\n"
        )


    # ==================================================
    # DOWNLOAD
    # ==================================================

    st.divider()

    st.header("📥 Save Your Notes")

    st.download_button(
        "⬇️ Download Study Notes",
        data=share_content,
        file_name="snap_and_study_notes.txt",
        mime="text/plain",
        use_container_width=True
    )


    # ==================================================
    # EMAIL
    # ==================================================

    st.divider()

    st.header("📧 Share Through Email")

    with st.form("email_form"):

        recipient_email = st.text_input(
            "Recipient email address"
        )

        email_submit = st.form_submit_button(
            "Send Study Notes"
        )

    if email_submit:

        if not re.fullmatch(
            r"[^@\s]+@[^@\s]+\.[^@\s]+",
            recipient_email.strip()
        ):

            st.warning("Enter a valid email address.")

        else:

            try:

                resend.api_key = st.secrets[
                    "RESEND_API_KEY"
                ]

                resend.Emails.send({
                    "from": "Snap & Study <onboarding@resend.dev>",
                    "to": [recipient_email.strip()],
                    "subject": "Your Snap & Study Learning Notes",
                    "text": share_content
                })

                st.success(
                    "Email request submitted successfully!"
                )

            except Exception as e:

                st.error(
                    f"Email sending failed: {str(e)}"
                )


    # ==================================================
    # WHATSAPP
    # ==================================================

    st.divider()

    st.header("🟢 Share Through WhatsApp")

    whatsapp_number = st.text_input(
        "WhatsApp number with country code",
        placeholder="Example: 919876543210"
    )

    if whatsapp_number.strip():

        if re.fullmatch(
            r"[0-9]{10,15}",
            whatsapp_number.strip()
        ):

            whatsapp_url = (
                f"https://wa.me/{whatsapp_number.strip()}"
                f"?text={quote(share_content)}"
            )

            st.link_button(
                "Open WhatsApp",
                whatsapp_url,
                use_container_width=True
            )

        else:

            st.info(
                "Enter a valid number with country code."
            )


    # ==================================================
    # TELEGRAM
    # ==================================================

    st.divider()

    st.header("✈️ Share Through Telegram")

    telegram_chat_id = st.text_input(
        "Telegram recipient Chat ID"
    )

    if st.button(
        "Send Notes to Telegram",
        use_container_width=True
    ):

        if not telegram_chat_id.strip():

            st.warning(
                "Please enter the recipient Chat ID."
            )

        else:

            try:

                bot_token = st.secrets[
                    "TELEGRAM_BOT_TOKEN"
                ]

                telegram_url = (
                    f"https://api.telegram.org/"
                    f"bot{bot_token}/sendMessage"
                )

                chunks = split_telegram_content(
                    share_content
                )

                for chunk in chunks:

                    response = requests.post(
                        telegram_url,
                        data={
                            "chat_id": telegram_chat_id.strip(),
                            "text": chunk
                        },
                        timeout=20
                    )

                    response.raise_for_status()

                    result = response.json()

                    if not result.get("ok"):

                        raise Exception(
                            result.get(
                                "description",
                                "Telegram API error"
                            )
                        )

                st.success(
                    "Study notes sent successfully!"
                )

            except Exception as e:

                st.error(
                    f"Telegram sending failed: {str(e)}"
                )


# ==================================================
# FOOTER
# ==================================================

st.divider()

st.markdown(
    "<p style='text-align:center;color:#94a3b8;'>"
    "Snap & Study | Your Personal AI Learning Assistant"
    "<br>"
    "Learn smarter. Understand better. Grow every day. ❤️"
    "</p>",
    unsafe_allow_html=True
)