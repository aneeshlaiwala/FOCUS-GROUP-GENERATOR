# Focus Group Discussion Generator

An AI-powered tool that generates synthetic focus group discussion transcripts with natural conversation flow, local dialects, and cultural authenticity.

## 🚀 Live Demo
**Streamlit Cloud URL**: [Your app will be available at](https://your-app-name.streamlit.app)

## ✨ Features
- **Multi-AI Provider Support**: OpenAI, Anthropic, Google, Cohere, Mistral
- **Language Support**: English, Hindi, Hinglish, French, Spanish, and more
- **Cultural Authenticity**: Local dialects, cultural references, natural speech patterns
- **Smart Recommendations**: AI provider suggestions based on language selection
- **Word Count Calculation**: Scientific estimation based on discussion duration
- **Export Options**: Download as TXT or DOCX files
- **File Upload**: Support for study objective documents (PDF, DOCX)

## 🛠️ Deployment on Streamlit Cloud

### Step 1: Prepare Your GitHub Repository

1. **Fork/Clone this repository** to your GitHub account
2. **Upload your files** with this structure:
```
focus-group-generator/
├── app.py                      # Main Streamlit application
├── requirements.txt            # Python dependencies
├── packages.txt               # System packages
├── README.md                  # This file
├── .streamlit/
│   ├── config.toml           # Streamlit configuration
│   └── secrets.toml.example  # Example secrets file
├── components/
│   ├── ai_providers.py       # AI provider integrations
│   ├── transcript_generator.py  # Core generation logic
│   └── utils.py              # Utility functions
└── data/
    └── language_profiles.json  # Language and dialect data
```

### Step 2: Setup Streamlit Cloud

1. **Go to** [share.streamlit.io](https://share.streamlit.io)
2. **Connect your GitHub** account
3. **Select your repository**: `your-username/focus-group-generator`
4. **Set main file path**: `app.py`
5. **Set branch**: `main` (or your default branch)

### Step 3: Configure Secrets in Streamlit Cloud

In your Streamlit Cloud app settings, add these secrets:

```toml
[api_keys]
OPENAI_API_KEY = "sk-your-actual-openai-key"
ANTHROPIC_API_KEY = "sk-ant-your-actual-anthropic-key"
GOOGLE_AI_API_KEY = "your-actual-google-key"
COHERE_API_KEY = "your-actual-cohere-key"
MISTRAL_API_KEY = "your-actual-mistral-key"

[app_config]
DEBUG_MODE = false
MAX_FILE_SIZE_MB = 10
```

### Step 4: Deploy

1. **Click "Deploy"** in Streamlit Cloud
2. **Wait for deployment** (usually 2-5 minutes)
3. **Your app will be live** at `https://your-app-name.streamlit.app`

## 🔑 Getting API Keys

### OpenAI
1. Visit [platform.openai.com](https://platform.openai.com)
2. Sign up/Login → Go to API Keys
3. Create new secret key
4. Format: `sk-xxxxxxxxxxxxxxxx`

### Anthropic Claude
1. Visit [console.anthropic.com](https://console.anthropic.com)
2. Sign up/Login → API Keys
3. Generate new key
4. Format: `sk-ant-xxxxxxxxxxxxxx`

### Google AI (Gemini)
1. Visit [aistudio.google.com](https://aistudio.google.com)
2. Sign up/Login → Get API Key
3. Create API key
4. Format: 39 characters

### Cohere
1. Visit [dashboard.cohere.ai](https://dashboard.cohere.ai)
2. Sign up/Login → API Keys
3. Generate trial key (free tier available)
4. Format: 40+ characters

### Mistral AI
1. Visit [console.mistral.ai](https://console.mistral.ai)
2. Sign up/Login → API Keys
3. Create new key
4. Format: 32 characters

## 📊 AI Provider Recommendations

| Language Combination | Recommended Provider | Reason |
|----------------------|---------------------|---------|
| English only | OpenAI GPT-4 | Best overall performance |
| Hindi/Hinglish | Google Gemini | Superior Indian language support |
| French only | Mistral AI | Native French excellence |
| Mixed European | Anthropic Claude | Consistent multi-language output |
| Business contexts | Cohere | Optimized for professional scenarios |

## 💰 Cost Estimation (per 1000 words)

| Provider | Model | Cost | Free Tier |
|----------|-------|------|-----------|
| Google AI | Gemini Pro | $0.0005 | 60 requests/min |
| Mistral | Large | $0.006 | Limited trial |
| Cohere | Command | $0.015 | 5K calls/month |
| OpenAI | GPT-4 Turbo | $0.03 | $5 credit |
| Anthropic | Claude 3 Sonnet | $0.015 | $5 credit |

## 🔧 Local Development

### Prerequisites
- Python 3.8+
- Git

### Setup
```bash
# Clone repository
git clone https://github.com/your-username/focus-group-generator.git
cd focus-group-generator

# Install dependencies
pip install -r requirements.txt

# Setup secrets
cp .streamlit/secrets.toml.example .streamlit/secrets.toml
# Edit secrets.toml with your API keys

# Run application
streamlit run app.py
```

## 📁 File Structure Details

### `app.py` - Main Application
```python
import streamlit as st
from components.ai_providers import AIProviderManager
from components.transcript_generator import TranscriptGenerator

# Main Streamlit app with multi-page layout
# Handles user input, API configuration, and transcript generation
```

### `components/ai_providers.py` - AI Integration
```python
class AIProviderManager:
    """Manages all AI provider integrations and model selection"""
    
    def __init__(self):
        self.providers = {
            'openai': OpenAIProvider(),
            'anthropic': AnthropicProvider(),
            'google': GoogleProvider(),
            'cohere': CohereProvider(),
            'mistral': MistralProvider()
        }
```

### `components/transcript_generator.py` - Core Logic
```python
class TranscriptGenerator:
    """Generates focus group transcripts with natural conversation flow"""
    
    def generate_transcript(self, config, prompt):
        # Research topic online
        # Generate participant personas
        # Create natural conversation flow
        # Apply language/dialect patterns
        # Format final transcript
```

## 🚨 Troubleshooting

### Common Issues

**1. Deployment Fails**
```bash
# Check requirements.txt formatting
# Ensure all dependencies have version numbers
# Verify packages.txt has correct system packages
```

**2. API Key Errors**
- Verify key format matches provider requirements
- Check key permissions and rate limits
- Ensure secrets are properly configured in Streamlit Cloud

**3. File Upload Issues**
- Maximum file size: 200MB (Streamlit limit)
- Supported formats: PDF, DOCX, DOC, TXT
- Check file encoding for non-English documents

**4. Generation Takes Too Long**
- Switch to faster models (GPT-3.5, Claude Haiku)
- Reduce transcript duration
- Check API rate limits

### Performance Optimization

**Caching**
```python
@st.cache_data
def load_language_profiles():
    """Cache language profiles for better performance"""
    
@st.cache_resource
def initialize_ai_providers():
    """Cache AI provider initialization"""
```

**Memory Management**
```python
# Clear large variables after use
del transcript_data
gc.collect()
```

## 📞 Support

### Getting Help
1. **GitHub Issues**: Report bugs or request features
2. **Streamlit Community**: [discuss.streamlit.io](https://discuss.streamlit.io)
3. **AI Provider Support**: Check respective documentation links

### Contributing
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## 📜 License

MIT License - feel free to use this tool for commercial and non-commercial purposes.

## 🌟 Acknowledgments

- **Streamlit**: For the amazing deployment platform
- **AI Providers**: OpenAI, Anthropic, Google, Cohere, Mistral
- **Open Source Libraries**: All the Python packages that make this possible

---

**Happy Focus Group Generating! 🎯📊**