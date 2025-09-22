# 🏔️ Zenith Mental Wellness Platform

An AI-powered mental wellness platform providing compassionate support, guided meditation, and community connection with multilingual capabilities.

![Zenith Logo](static/assets/logo.svg)

## 🌟 Features

### Core Capabilities
- **AI Companion (Zenith)**: Compassionate mental wellness guide with empathetic responses
- **Multilingual Support**: 10+ Indian languages supported
- **Crisis Detection**: Real-time monitoring and immediate support resources
- **Guided Meditation**: Breathing exercises, mindfulness practices, and timer
- **Peer Community**: Anonymous support network
- **Spiritual Wisdom**: Daily quotes, affirmations, and spiritual guidance
- **Mood Tracking**: Monitor emotional well-being over time

### Zenith AI Persona
- Warm, nurturing, and genuinely caring companion
- Validates emotions before offering guidance
- Provides guided breathing exercises in-chat
- Seamlessly integrates wellness resources
- Offers uplifting quotes and affirmations

## 🚀 Quick Start

### Prerequisites
- Python 3.10 or higher
- Node.js (optional, for frontend development)
- Firebase account (for authentication)
- Google Cloud account (for AI services)

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/yourusername/zenith-wellness-platform.git
cd zenith-wellness-platform
```

2. **Create and activate virtual environment**
```bash
python -m venv venv

# On Windows
venv\Scripts\activate

# On Unix/MacOS
source venv/bin/activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Set up environment variables**

Create a `.env` file in the root directory:
```env
# Google AI Services
GOOGLE_API_KEY=
GEMINI_CUSTOM_MODEL_ID=gemini-2.5-flash
GOOGLE_APPLICATION_CREDENTIALS=

# Firebase Configuration
FIREBASE_SERVICE_ACCOUNT_KEY_PATH=
FIREBASE_API_KEY=
FIREBASE_AUTH_DOMAIN=
FIREBASE_PROJECT_ID=
FIREBASE_STORAGE_BUCKET=
FIREBASE_MESSAGING_SENDER_ID=
FIREBASE_APP_ID=

# Security
SECRET_KEY=your_secret_key_here
JWT_SECRET_KEY=a-string-secret-at-least-256-bits-long
JWT_ALGORITHM=HS256
JWT_EXPIRATION_MINUTES=1440

# Application Settings
CORS_ORIGINS=["http://localhost:8000", "http://127.0.0.1:8000"]
SUPPORTED_LANGUAGES=["en", "hi", "bn", "te", "mr", "ta", "ur", "gu", "kn", "ml"]
```

5. **Add Firebase Service Account**

Place your Firebase service account JSON file in the `credentials/` directory:
```bash
credentials/firebase-service-account.json
```

6. **Run the application**
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

7. **Access the application**

Open your browser and navigate to:
- Application: http://localhost:8000
- API Documentation: http://localhost:8000/docs
- Alternative API Docs: http://localhost:8000/redoc

## 🏗️ Project Structure

```
zenith-wellness-platform/
├── app/
│   ├── api/
│   │   ├── endpoints/       # API endpoints
│   │   │   ├── auth.py      # Authentication
│   │   │   ├── chat.py      # AI chat
│   │   │   ├── chat_enhanced.py  # Enhanced Zenith chat
│   │   │   ├── crisis.py    # Crisis support
│   │   │   ├── community.py # Community features
│   │   │   ├── spiritual.py # Spiritual wisdom
│   │   │   └── meditation.py # Meditation features
│   │   ├── dependencies.py  # API dependencies
│   │   └── router.py        # Main router
│   ├── core/
│   │   ├── config.py       # Configuration
│   │   └── security.py     # Security utilities
│   ├── models/             # Data models
│   ├── services/           # Business logic
│   │   ├── ai_service.py   # AI services
│   │   └── firebase_service.py # Firebase integration
│   └── main.py            # FastAPI application
├── static/                # Frontend files
│   ├── index.html        # Main application
│   ├── homepage.html     # Homepage template
│   ├── css/              # Stylesheets
│   │   ├── styles.css    # Main styles
│   │   ├── sidebar.css   # Navigation styles
│   │   ├── chat.css      # Chat interface
│   │   ├── meditation.css # Meditation features
│   │   └── homepage.css  # Homepage styles
│   ├── js/               # JavaScript files
│   │   ├── app.js        # Main application logic
│   │   ├── api.js        # API client
│   │   ├── auth.js       # Authentication
│   │   ├── chat.js       # Chat functionality
│   │   ├── meditation.js # Meditation features
│   │   └── spiritual.js  # Spiritual features
│   └── assets/           # Images and icons
│       └── logo.svg      # Zenith logo
├── credentials/          # Service account files
├── requirements.txt      # Python dependencies
├── .env                 # Environment variables
└── README.md           # This file
```

## 💬 Using Zenith AI Companion

### Example Interactions

**User:** "I'm feeling really stressed about work"

**Zenith:** 
> I hear you, and that sounds incredibly challenging. Work stress can be overwhelming, and it's completely understandable to feel this way. 
>
> Remember: "Every storm runs out of rain." 🌤️
>
> Let's take a moment together right now. Find a comfortable position and let's do a quick breathing exercise:
> - Take a deep breath in through your nose for 4 counts... 
> - Hold it gently for 4 counts...
> - Now exhale slowly through your mouth for 4 counts...
> - Let's do this two more times together.
>
> How are you feeling now? If you'd like more guided exercises, our Meditation section has wonderful resources for stress relief. The Community section also has others who understand what you're going through.

### Wellness Protocol
When users express distress, Zenith follows a structured approach:
1. **Validates feelings** with empathy
2. **Shares an uplifting quote** relevant to the situation
3. **Guides through breathing exercises** step-by-step
4. **References app features** naturally
5. **Offers alternatives** and escalation paths

## 🧪 Testing

### Test the API endpoints
```bash
# Health check
curl http://localhost:8000/health

# API documentation
curl http://localhost:8000/api
```

### Test Chat Functionality
1. Open the application in your browser
2. Click "Continue as Guest" or create an account
3. Navigate to "AI Companion"
4. Try these test messages:
   - "I'm feeling stressed"
   - "Guide me through a breathing exercise"
   - "Tell me something uplifting"

### Test Features
- **Meditation**: Start a timed session with visual progress
- **Spiritual Wisdom**: Click "New Quote" for inspiration
- **Community**: Create and interact with posts
- **Crisis Support**: Test with keywords to see resources

## 🔒 Security Features

- JWT-based authentication
- Firebase security rules
- CORS protection
- Environment variable management
- Secure password hashing
- Crisis keyword monitoring

## 🌍 Supported Languages

- English (en)
- Hindi (हिन्दी)
- Bengali (বাংলা)
- Telugu (తెలుగు)
- Marathi (मराठी)
- Tamil (தமிழ்)
- Urdu (اردو)
- Gujarati (ગુજરાતી)
- Kannada (ಕನ್ನಡ)
- Malayalam (മലയാളം)

## 📱 Responsive Design

The platform is fully responsive with:
- Mobile-optimized navigation
- Touch-friendly interfaces
- Adaptive layouts
- Progressive enhancement

## 🚧 Coming Soon

- **Video Therapy Sessions**: Connect with licensed therapists
- **Advanced Analytics**: Track mental health journey
- **Group Therapy**: Moderated group sessions
- **Biometric Integration**: Mood tracking via wearables
- **AI-Powered Journaling**: Guided reflection exercises

## 🤝 Contributing

We welcome contributions! Please see our contributing guidelines for more details.

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Crisis Resources

If you or someone you know is in crisis, please reach out:

- **NIMHANS**: 080-46110007 (24/7)
- **Vandrevala Foundation**: 9999666555 (24/7)
- **AASRA**: 91-9820466726 (24/7)
- **Emergency Services**: 112

## 🙏 Acknowledgments

- Google Gemini AI for powering Zenith
- Firebase for authentication and data storage
- The mental health community for guidance
- All contributors and supporters

---

**Remember:** Zenith is a supportive companion, not a replacement for professional mental health care. If you're experiencing severe mental health issues, please seek help from qualified professionals.

Built with ❤️ for mental wellness
