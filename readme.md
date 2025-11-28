# Munimji.ai - Your Personal Account Buddy for Your Business!

(WhatsApp-based AI accountant: FastAPI + Meta Cloud API + Docker + LangGraph + fine-tuned IndicBERT/MuRIL + PostgreSQL + Whisper)

Ever wonder where all your company profits go? I'm here to help you figure that out.

Just send me your sales, buys, and credit (*udhaar*) on WhatsApp—even quick text or voice notes—and I'll keep track for you.

Share your bills and challans however it's easiest: a quick photo, a PDF, or a forward from your email. I'll log it and keep your accounts perfectly updated.

**No spreadsheets. No stress. Just a clear picture of your business finances, right in your chat.**

## Features

**➕ Log any transaction →** send me a message, photo of a bill, or even a voice note:
> *"Ramesh ko ₹500 ka udhaar diya"*
> *"Aaj ka cash sale ₹2500"*

**📅 Get a daily summary →** ask about today's business:
> *"Aaj ka hisaab batao?"*
> *"What was the total sale today?"*

**📈 Ask for business reports →** see your weekly profit or a customer's balance:
> *"Iss hafte ka profit kitna hai?"*
> *"Ramesh ka total baaki kitna hai?"*

## Prerequisites

- Python 3.12 or higher
- PostgreSQL database (local or cloud)
- WhatsApp Business API account (for production)
- Google AI API key (for Gemini model)
- uv package manager (recommended)

## Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/rajatrsrivastav/munimji.git
   cd munimji
   ```

2. **Install uv (if not already installed):**
   ```bash
   curl -LsSf https://astral.sh/uv/install.sh | sh
   ```

3. **Create virtual environment and install dependencies:**
   ```bash
   uv sync
   ```

4. **Activate the virtual environment:**
   ```bash
   source .venv/bin/activate
   ```

## Environment Setup

1. **Copy environment template:**
   ```bash
   cp .env.example .env
   ```

2. **Configure your `.env` file:**
   ```env
   # Database
   DATABASE_URL=postgresql://username:password@localhost:5432/munimji

   # WhatsApp API (get from Meta Developer Console)
   ACCESS_TOKEN=your_whatsapp_access_token
   APP_SECRET=your_whatsapp_app_secret
   PHONE_NUMBER_ID=your_whatsapp_phone_number_id
   WEBHOOK_VERIFY_TOKEN=your_custom_verify_token

   # AI Models
   GOOGLE_API_KEY=your_google_ai_api_key

   # Optional: Groq API for Whisper (if using Groq)
   GROQ_API_KEY=your_groq_api_key

   # App Settings
   GRAPH_API_VERSION=v16.0
   PORT=5000
   DEV_RELOAD=true
   ```

## Database Setup

1. **Create PostgreSQL database:**
   ```sql
   CREATE DATABASE munimji;
   CREATE USER munimji_user WITH PASSWORD 'your_password';
   GRANT ALL PRIVILEGES ON DATABASE munimji TO munimji_user;
   ```

2. **Run database migrations:**
   ```bash
   uv run alembic upgrade head
   ```

   Or if you prefer using alembic directly:
   ```bash
   source .venv/bin/activate
   alembic upgrade head
   ```

## Running the Application

### Development Mode

1. **Start the FastAPI server:**
   ```bash
   uv run uvicorn backend.whatsapp.app:app --reload --host 0.0.0.0 --port 5000
   ```

2. **Test the webhook endpoint:**
   - Visit `http://localhost:5000/docs` for API documentation
   - Use ngrok or similar to expose the webhook for WhatsApp

### Using Streamlit (for testing chatbot)

```bash
uv run streamlit run backend/chatbot_backend/app.py
```

## WhatsApp Setup (Production)

1. **Create a Meta Developer Account:**
   - Go to [Meta for Developers](https://developers.facebook.com/)
   - Create a new app with WhatsApp product

2. **Configure Webhook:**
   - Set webhook URL to your deployed app's `/webhook` endpoint
   - Verify token should match `WEBHOOK_VERIFY_TOKEN` in your `.env`

3. **Test the integration:**
   - Send "hi" to your WhatsApp Business number
   - Complete the onboarding flow

## Project Structure

```
munimji/
├── backend/
│   ├── whatsapp/           # WhatsApp integration
│   │   ├── app.py         # Main FastAPI app
│   │   ├── config.py      # Configuration
│   │   ├── handlers.py    # Webhook handlers
│   │   ├── utils.py       # Utility functions
│   │   ├── media.py       # Media processing
│   │   ├── chatbot.py     # Chatbot integration
│   │   ├── audio_processor.py
│   │   └── image_processor.py
│   └── chatbot_backend/   # LangGraph chatbot
│       ├── app.py
│       └── db/           # Database models
├── migrations/           # Alembic migrations
├── downloads/           # Temporary file storage
├── pyproject.toml       # Project configuration
├── uv.lock             # Dependency lock file
└── alembic.ini         # Migration config
```

## Testing

1. **Install dev dependencies:**
   ```bash
   uv sync --group dev
   ```

2. **Run unit tests:**
   ```bash
   uv run pytest
   ```

3. **Test WhatsApp integration:**
   - Use the `/send_text_demo` endpoint to send test messages
   - Check database for user and conversation records

## Deployment

### Docker (Recommended)

1. **Build the image:**
   ```bash
   docker build -t munimji .
   ```

2. **Run with Docker:**
   ```bash
   docker run -p 5000:5000 --env-file .env munimji
   ```

### Cloud Deployment

- **Railway:** Connect GitHub repo for automatic deployment
- **Render:** Use the Dockerfile for deployment
- **AWS/GCP:** Use ECS/EKS or Cloud Run with PostgreSQL

## Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/your-feature`
3. Make your changes and test thoroughly
4. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For questions or issues:
- Open an issue on GitHub
- Check the technical documentation in `TEACHNICAL.md`