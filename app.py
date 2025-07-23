import streamlit as st
import pandas as pd
import io
import json
import time
from datetime import datetime
from pathlib import Path

# Import custom components (you'll create these)
try:
    from components.ai_providers import AIProviderManager
    from components.transcript_generator import TranscriptGenerator
    from components.utils import (
        calculate_word_count, 
        validate_api_key, 
        export_to_docx,
        export_to_txt,
        process_uploaded_file
    )
except ImportError:
    st.error("Missing component files. Please ensure all components are properly uploaded.")
    st.stop()

# Page configuration
st.set_page_config(
    page_title="Focus Group Generator",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state
if 'step' not in st.session_state:
    st.session_state.step = 'form'
if 'generated_prompt' not in st.session_state:
    st.session_state.generated_prompt = ""
if 'generated_transcript' not in st.session_state:
    st.session_state.generated_transcript = ""
if 'api_config' not in st.session_state:
    st.session_state.api_config = {}

# AI Provider configurations
AI_PROVIDERS = {
    'openai': {
        'name': 'OpenAI',
        'models': ['gpt-4-turbo', 'gpt-4', 'gpt-3.5-turbo'],
        'languages': ['English', 'Hindi', 'Hinglish', 'French', 'Spanish', 'Mandarin', 'Arabic'],
        'usps': ['Best overall performance', 'Superior English & Hinglish', 'Realistic character development'],
        'cost_per_1k': '$0.03-0.06'
    },
    'anthropic': {
        'name': 'Anthropic Claude',
        'models': ['claude-3-opus-20240229', 'claude-3-sonnet-20240229', 'claude-3-haiku-20240307'],
        'languages': ['English', 'French', 'Spanish', 'Portuguese'],
        'usps': ['Best at following complex prompts', 'Superior consistency', 'Excellent character traits'],
        'cost_per_1k': '$0.015-0.075'
    },
    'google': {
        'name': 'Google AI (Gemini)',
        'models': ['gemini-pro', 'gemini-pro-vision'],
        'languages': ['English', 'Hindi', 'Hinglish', 'French', 'Spanish', 'Mandarin', 'Arabic', 'Portuguese'],
        'usps': ['Best for Hindi & Indian languages', 'Strong cultural context', 'Excellent regional dialects'],
        'cost_per_1k': '$0.0005-0.002'
    },
    'cohere': {
        'name': 'Cohere',
        'models': ['command', 'command-light'],
        'languages': ['English', 'French', 'Spanish'],
        'usps': ['Best conversation coherence', 'Excellent for business scenarios', 'Strong logical flow'],
        'cost_per_1k': '$0.015-0.025'
    },
    'mistral': {
        'name': 'Mistral AI',
        'models': ['mistral-large-latest', 'mistral-medium-latest', 'mistral-small-latest'],
        'languages': ['English', 'French', 'Spanish', 'Portuguese'],
        'usps': ['Best for French language', 'Superior European cultural nuances', 'French-speaking regions'],
        'cost_per_1k': '$0.0002-0.006'
    }
}

def get_recommended_provider(selected_languages):
    """Get recommended AI provider based on selected languages"""
    if 'Hindi' in selected_languages or 'Hinglish' in selected_languages:
        return 'google'
    elif len(selected_languages) == 1 and 'French' in selected_languages:
        return 'mistral'
    elif len(selected_languages) == 1 and 'English' in selected_languages:
        return 'openai'
    else:
        return 'openai'  # Default for mixed languages

def render_api_configuration():
    """Render the AI provider configuration section"""
    st.markdown("### 🤖 AI Provider Configuration")
    
    # Get form data from session state
    selected_languages = st.session_state.get('languages', ['English'])
    recommended_provider = get_recommended_provider(selected_languages)
    
    # Show recommendation
    st.info(f"💡 **Recommended for your languages ({', '.join(selected_languages)}):** {AI_PROVIDERS[recommended_provider]['name']}")
    
    # Provider selection
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("#### Select AI Provider")
        
        # Create provider cards
        selected_provider = st.radio(
            "Choose your AI provider:",
            options=list(AI_PROVIDERS.keys()),
            format_func=lambda x: AI_PROVIDERS[x]['name'],
            index=list(AI_PROVIDERS.keys()).index(recommended_provider),
            key="selected_provider"
        )
        
        # Show provider details
        provider_info = AI_PROVIDERS[selected_provider]
        
        # Language support
        st.markdown("**Language Support:**")
        lang_status = []
        for lang in provider_info['languages']:
            if lang in selected_languages:
                lang_status.append(f"✅ {lang}")
            else:
                lang_status.append(f"⚫ {lang}")
        st.write(" | ".join(lang_status))
        
        # USPs
        st.markdown("**Key Strengths:**")
        for usp in provider_info['usps']:
            st.write(f"• {usp}")
        
        st.markdown(f"**Cost:** {provider_info['cost_per_1k']} per 1000 words")
    
    with col2:
        st.markdown("#### Provider Comparison")
        comparison_data = []
        for key, provider in AI_PROVIDERS.items():
            lang_support = len([l for l in provider['languages'] if l in selected_languages])
            comparison_data.append({
                'Provider': provider['name'],
                'Languages': f"{lang_support}/{len(selected_languages)}",
                'Cost': provider['cost_per_1k']
            })
        
        df = pd.DataFrame(comparison_data)
        st.dataframe(df, use_container_width=True)
    
    # Model selection
    if selected_provider:
        st.markdown("#### Select Model")
        selected_model = st.selectbox(
            "Choose model:",
            options=provider_info['models'],
            key="selected_model"
        )
        
        # API Key input
        st.markdown("#### API Key")
        api_key = st.text_input(
            f"Enter your {provider_info['name']} API key:",
            type="password",
            key="api_key",
            help=f"Get your API key from the {provider_info['name']} dashboard"
        )
        
        # API key validation
        if api_key:
            if validate_api_key(selected_provider, api_key):
                st.success("✅ Valid API key format")
                # Store in session state
                st.session_state.api_config = {
                    'provider': selected_provider,
                    'model': selected_model,
                    'api_key': api_key
                }
            else:
                st.error("❌ Invalid API key format")
                st.session_state.api_config = {}
        
        # API documentation links
        docs_links = {
            'openai': 'https://platform.openai.com/docs',
            'anthropic': 'https://docs.anthropic.com',
            'google': 'https://ai.google.dev/docs',
            'cohere': 'https://docs.cohere.com',
            'mistral': 'https://docs.mistral.ai'
        }
        
        st.markdown(f"📚 [Get API Key & Documentation]({docs_links.get(selected_provider, '#')})")

def render_form():
    """Render the main input form"""
    st.title("🎯 Focus Group Discussion Generator")
    st.markdown("Generate realistic focus group transcripts with natural conversation flow, local dialects, and cultural authenticity.")
    
    # API Configuration
    with st.expander("🤖 AI Provider Configuration", expanded=True):
        render_api_configuration()
    
    st.markdown("---")
    
    # Participants Section
    st.markdown("### 👥 Participants")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        num_participants = st.number_input("Total Participants", min_value=4, max_value=12, value=8)
    with col2:
        male_count = st.number_input("Male", min_value=0, max_value=num_participants, value=4)
    with col3:
        female_count = st.number_input("Female", min_value=0, max_value=num_participants, value=4)
    with col4:
        non_binary_count = st.number_input("Non-Binary", min_value=0, max_value=num_participants, value=0)
    
    # Validation
    total_gender = male_count + female_count + non_binary_count
    if total_gender != num_participants:
        st.error(f"Gender counts ({total_gender}) don't match total participants ({num_participants})")
    
    age_range = st.text_input("Age Range", value="25-45", help="e.g., 25-45 or 18-25, 35-50")
    
    demographics = st.text_area(
        "Demographic Profile", 
        height=100,
        help="Describe occupation, income group, education, lifestyle details, etc.",
        placeholder="e.g., Urban professionals, middle-income, college-educated, tech-savvy..."
    )
    
    # Study Details Section
    st.markdown("### 🎯 Study Details")
    
    topic = st.text_input(
        "Topic of Discussion", 
        help="e.g., Electric Vehicle Adoption in Tier 2 Cities",
        placeholder="Enter your research topic..."
    )
    
    objective = st.text_area(
        "Objective of Study", 
        height=100,
        help="Describe the research objectives and what you want to learn",
        placeholder="What insights are you trying to gather from this focus group?"
    )
    
    # File upload for study documents
    uploaded_file = st.file_uploader(
        "Upload Study Document (Optional)", 
        type=['pdf', 'docx', 'doc', 'txt'],
        help="Upload additional context about your study objectives"
    )
    
    # Duration and Location
    col1, col2 = st.columns(2)
    
    with col1:
        duration = st.number_input("Duration (minutes)", min_value=15, max_value=180, value=60)
        estimated_words = calculate_word_count(duration)
        st.info(f"📊 Estimated words: ~{estimated_words:,}")
    
    with col2:
        location = st.text_input(
            "Location Profile", 
            help="e.g., Mumbai, India or Quebec, Canada",
            placeholder="City, Country or Region"
        )
    
    # Discussion Type
    discussion_type = st.radio(
        "Type of Discussion",
        options=['Online', 'Offline'],
        horizontal=True
    )
    
    # Language Selection
    st.markdown("### 🌐 Language Selection")
    
    available_languages = ['English', 'Hindi', 'Hinglish', 'French', 'Spanish', 'Mandarin', 'Arabic', 'Portuguese']
    
    selected_languages = st.multiselect(
        "Select Discussion Language(s)",
        options=available_languages,
        default=['English']
    )
    
    # Store form data in session state
    st.session_state.form_data = {
        'num_participants': num_participants,
        'male_count': male_count,
        'female_count': female_count,
        'non_binary_count': non_binary_count,
        'age_range': age_range,
        'demographics': demographics,
        'topic': topic,
        'objective': objective,
        'duration': duration,
        'location': location,
        'discussion_type': discussion_type.lower(),
        'languages': selected_languages,
        'uploaded_file': uploaded_file
    }
    st.session_state.languages = selected_languages  # For API provider recommendation
    
    # Generate button
    st.markdown("---")
    
    # Validation checks
    required_fields = [topic, objective, location]
    api_configured = bool(st.session_state.api_config.get('api_key'))
    
    if st.button("🚀 Generate Research Prompt", type="primary", use_container_width=True):
        if not all(required_fields):
            st.error("❌ Please fill in all required fields: Topic, Objective, and Location")
        elif not api_configured:
            st.error("❌ Please configure your AI provider and API key")
        elif total_gender != num_participants:
            st.error("❌ Gender counts don't match total participants")
        else:
            st.session_state.step = 'prompt'
            st.rerun()

def render_prompt_page():
    """Render the prompt review and edit page"""
    st.title("📝 Review & Edit Generated Prompt")
    st.markdown("Review the generated prompt below. You can edit it before final submission.")
    
    # Generate prompt if not already generated
    if not st.session_state.generated_prompt:
        with st.spinner("🔍 Researching topic and generating prompt..."):
            # Simulate prompt generation
            form_data = st.session_state.form_data
            estimated_words = calculate_word_count(form_data['duration'])
            
            prompt = f"""FOCUS GROUP DISCUSSION GENERATOR PROMPT

STUDY CONFIGURATION:
- Participants: {form_data['num_participants']} total ({form_data['male_count']}M, {form_data['female_count']}F, {form_data['non_binary_count']}NB)
- Age Range: {form_data['age_range']}
- Demographics: {form_data['demographics']}
- Topic: {form_data['topic']}
- Objective: {form_data['objective']}
- Duration: {form_data['duration']} minutes (Target: ~{estimated_words:,} words)
- Location: {form_data['location']}
- Type: {form_data['discussion_type']}
- Languages: {', '.join(form_data['languages'])}

RESEARCH REQUIREMENTS:
1. Research the topic "{form_data['topic']}" thoroughly for {form_data['location']}
2. Understand local market conditions, cultural nuances, and recent developments
3. Generate realistic participant personas based on demographics and location
4. Create natural conversation flow with local dialects and speech patterns

TRANSCRIPT STRUCTURE:
1. Opening (15% - {int(estimated_words * 0.15):,} words):
   - Welcome and introductions
   - Ground rules and recording consent
   - Overview of discussion

2. Warm-up (10% - {int(estimated_words * 0.10):,} words):
   - Icebreaker questions
   - General topic introduction

3. Core Discussion (65% - {int(estimated_words * 0.65):,} words):
   - Main research questions
   - Deep probing and follow-ups
   - Natural participant interactions

4. Closing (10% - {int(estimated_words * 0.10):,} words):
   - Summary of key points
   - Final thoughts
   - Thank you and wrap-up

NATURAL SPEECH REQUIREMENTS:
- Include natural speech patterns: "umm", "you know", "like"
- Add grammatical imperfections and hesitations
- Use local references and cultural context from {form_data['location']}
- Include appropriate dialect/accent markers for {'/'.join(form_data['languages'])}
- Show realistic group dynamics (interruptions, agreements, disagreements)

MODERATOR BEHAVIOR:
- Maintain neutrality throughout
- Use probing questions: "Can you tell me more about that?", "What do others think?"
- Manage participation: encourage quiet members, tactfully redirect dominant ones
- Bridge between topics smoothly
- Summarize and reflect back key points

PARTICIPANT PERSONAS:
Generate {form_data['num_participants']} distinct personalities with:
- Realistic names appropriate for {form_data['location']}
- Varied speaking styles and opinions
- Different levels of engagement
- Authentic demographic representation

OUTPUT FORMAT:
Generate a realistic focus group transcript with:
- Timestamp markers every 5-10 minutes
- Speaker identification (Moderator, Participant names)
- Natural conversation flow
- Realistic pace and word count distribution
- Cultural authenticity and local relevance
"""
            
            st.session_state.generated_prompt = prompt
    
    # Editable prompt
    edited_prompt = st.text_area(
        "Generated Prompt (Editable)",
        value=st.session_state.generated_prompt,
        height=400,
        help="You can edit this prompt before generating the transcript"
    )
    
    # Update session state with edited prompt
    st.session_state.generated_prompt = edited_prompt
    
    # Action buttons
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("← Back to Form", use_container_width=True):
            st.session_state.step = 'form'
            st.rerun()
    
    with col2:
        if st.button("🎬 Generate Transcript", type="primary", use_container_width=True):
            st.session_state.step = 'generating'
            st.rerun()

def render_generating_page():
    """Render the transcript generation page with progress"""
    st.title("🎬 Generating Your Focus Group Transcript")
    
    # Progress indicators
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    # Simulate generation process
    if not st.session_state.generated_transcript:
        
        # Stage 1: Research
        status_text.text("🔍 Researching topic and market conditions...")
        progress_bar.progress(20)
        time.sleep(2)
        
        # Stage 2: Persona Creation
        status_text.text("👥 Creating participant personas...")
        progress_bar.progress(40)
        time.sleep(2)
        
        # Stage 3: Cultural Context
        status_text.text("🌍 Analyzing cultural context and local references...")
        progress_bar.progress(60)
        time.sleep(2)
        
        # Stage 4: Transcript Generation
        status_text.text("💬 Generating natural conversation flow...")
        progress_bar.progress(80)
        time.sleep(3)
        
        # Stage 5: Final Processing
        status_text.text("✨ Finalizing transcript and applying language patterns...")
        progress_bar.progress(100)
        time.sleep(1)
        
        # Generate actual transcript (this would call the AI provider)
        form_data = st.session_state.form_data
        estimated_words = calculate_word_count(form_data['duration'])
        
        # Sample transcript generation
        transcript = f"""FOCUS GROUP DISCUSSION TRANSCRIPT
Topic: {form_data['topic']}
Date: {datetime.now().strftime('%B %d, %Y')}
Duration: {form_data['duration']} minutes
Location: {form_data['location']}
Type: {form_data['discussion_type'].upper()}

PARTICIPANTS:
- Moderator: Sarah Chen (Research Facilitator)
- P1: Amit Sharma (M, 32, Software Engineer)
- P2: Priya Patel (F, 29, Marketing Manager)
- P3: Rajesh Kumar (M, 45, Small Business Owner)
- P4: Sneha Singh (F, 26, Graduate Student)
- P5: David Thompson (M, 38, Consultant)
- P6: Maria Rodriguez (F, 31, Teacher)
- P7: Chen Wei (M, 27, Designer)
- P8: Aisha Khan (F, 35, Healthcare Worker)

---

[00:00] MODERATOR: Good {'morning' if form_data['discussion_type'] == 'online' else 'evening'} everyone, thank you for {'joining our virtual session' if form_data['discussion_type'] == 'online' else 'coming to our facility today'}. I'm Sarah, and I'll be moderating today's discussion about {form_data['topic']}. Before we begin, I want to assure you that everything discussed here will remain confidential and will only be used for research purposes.

[00:02] MODERATOR: {'Since we're meeting online, please make sure your audio is clear and feel free to use the chat if needed.' if form_data['discussion_type'] == 'online' else 'I see everyone has their name cards and refreshments. Please make yourselves comfortable.'} This session will last approximately {form_data['duration']} minutes, and we'll be recording for analysis purposes. Is everyone okay with that?

[Various participants nod and say "Yes"]

[00:03] MODERATOR: Excellent. Let's start with quick introductions. Amit, would you like to begin?

[00:04] P1 (AMIT): Hi everyone, I'm Amit Sharma. I work in software development here in {form_data['location']}. I've been, umm, quite interested in this topic actually, especially how it affects our daily lives.

[00:05] P2 (PRIYA): Hello! I'm Priya Patel, I work in marketing. This is quite relevant to my work, so I'm excited to share my thoughts. I've been following some trends in this space.

[00:06] P3 (RAJESH): Rajesh Kumar here. I run a small business, so I look at things from a different angle, you know? Cost, practicality, that sort of thing.

[00:07] P4 (SNEHA): Hi, I'm Sneha Singh. I'm finishing my master's degree, so I bring the younger perspective, I guess. *laughs* I've done quite a bit of research on this for my thesis actually.

[00:08] P5 (DAVID): David Thompson. I'm a consultant, so I work with various companies on strategy. This topic comes up a lot in my client discussions.

[00:09] P6 (MARIA): Maria Rodriguez, I'm a high school teacher. I see how these issues affect families and students, so that's my angle.

[00:10] P7 (CHEN): Chen Wei, I'm a UX designer. I think about user experience and how people actually interact with these... solutions, I suppose.

[00:11] P8 (AISHA): And I'm Aisha Khan, I work in healthcare. I'm interested in the health and safety aspects of what we're discussing today.

[00:12] MODERATOR: Thank you all for those introductions. Now, let's dive into our main topic. To start with something broad - when you first hear about "{form_data['topic']}", what comes to mind? Sneha, let's start with you.

[The transcript would continue with natural conversation flow, cultural references specific to {form_data['location']}, and realistic group dynamics for the full {form_data['duration']} minutes, totaling approximately {estimated_words:,} words]

---

TRANSCRIPT STATISTICS:
- Total Duration: {form_data['duration']} minutes
- Word Count: ~{estimated_words:,} words
- Participants: {form_data['num_participants']} people
- Languages: {', '.join(form_data['languages'])}
- Cultural References: {form_data['location']}-specific
- Natural Speech Patterns: Included throughout

MODERATOR NOTES:
- All participants actively engaged
- Good diversity of opinions observed
- Cultural context well-represented for {form_data['location']}
- Natural speech patterns and local references maintained throughout
- Realistic group dynamics with appropriate interruptions and agreements
"""
        
        st.session_state.generated_transcript = transcript
        status_text.text("✅ Transcript generation complete!")
    
    # Automatically move to results
    time.sleep(1)
    st.session_state.step = 'result'
    st.rerun()

def render_result_page():
    """Render the final transcript results page"""
    st.title("📄 Generated Focus Group Transcript")
    
    form_data = st.session_state.form_data
    estimated_words = calculate_word_count(form_data['duration'])
    
    # Action buttons at the top
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.download_button(
            label="📥 Download TXT",
            data=st.session_state.generated_transcript,
            file_name=f"focus_group_{form_data['topic'].replace(' ', '_')}.txt",
            mime="text/plain",
            use_container_width=True
        ):
            st.success("TXT file downloaded!")
    
    with col2:
        # Convert to DOCX format (simplified)
        docx_data = export_to_docx(st.session_state.generated_transcript, form_data)
        if st.download_button(
            label="📥 Download DOCX",
            data=docx_data,
            file_name=f"focus_group_{form_data['topic'].replace(' ', '_')}.docx",
            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            use_container_width=True
        ):
            st.success("DOCX file downloaded!")
    
    with col3:
        if st.button("🔄 Generate New", use_container_width=True):
            # Clear session state and start over
            for key in ['generated_prompt', 'generated_transcript']:
                if key in st.session_state:
                    del st.session_state[key]
            st.session_state.step = 'form'
            st.rerun()
    
    # Transcript statistics
    st.markdown("### 📊 Transcript Statistics")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Duration", f"{form_data['duration']} min")
    with col2:
        st.metric("Word Count", f"~{estimated_words:,}")
    with col3:
        st.metric("Participants", f"{form_data['num_participants']} people")
    with col4:
        st.metric("Languages", f"{len(form_data['languages'])}")
    
    # Additional statistics
    with st.expander("📈 Detailed Statistics"):
        word_breakdown = {
            'Opening (15%)': int(estimated_words * 0.15),
            'Warm-up (10%)': int(estimated_words * 0.10),
            'Core Discussion (65%)': int(estimated_words * 0.65),
            'Closing (10%)': int(estimated_words * 0.10)
        }
        
        stat_df = pd.DataFrame([
            {"Section": k, "Words": v, "Percentage": k.split('(')[1].split(')')[0]} 
            for k, v in word_breakdown.items()
        ])
        
        st.dataframe(stat_df, use_container_width=True)
    
    # Transcript display
    st.markdown("### 📄 Generated Transcript")
    
    # Search functionality
    search_term = st.text_input("🔍 Search in transcript:", placeholder="Enter keyword to search...")
    
    # Display transcript
    transcript_display = st.session_state.generated_transcript
    
    if search_term:
        # Highlight search terms (simplified)
        highlighted = transcript_display.replace(
            search_term, 
            f"**{search_term}**"
        )
        st.markdown(highlighted)
    else:
        st.text_area(
            "Transcript Content",
            value=transcript_display,
            height=400,
            disabled=True
        )
    
    # Feedback section
    st.markdown("---")
    st.markdown("### 💬 Feedback")
    
    rating = st.select_slider(
        "Rate the quality of generated transcript:",
        options=[1, 2, 3, 4, 5],
        value=4,
        format_func=lambda x: "⭐" * x
    )
    
    feedback = st.text_area("Additional feedback (optional):")
    
    if st.button("Submit Feedback"):
        st.success("Thank you for your feedback!")

# Main application logic
def main():
    """Main application entry point"""
    
    # Sidebar with navigation
    with st.sidebar:
        st.image("https://via.placeholder.com/150x50/3b82f6/white?text=FGG", width=150)
        st.markdown("### Navigation")
        
        # Progress indicator
        steps = ['Form', 'Prompt', 'Generate', 'Result']
        current_step_index = steps.index(st.session_state.step.title())
        
        for i, step in enumerate(steps):
            if i < current_step_index:
                st.markdown(f"✅ {step}")
            elif i == current_step_index:
                st.markdown(f"🔄 **{step}**")
            else:
                st.markdown(f"⏳ {step}")
        
        st.markdown("---")
        
        # Quick stats
        if 'form_data' in st.session_state:
            st.markdown("### Current Session")
            st.write(f"**Topic:** {st.session_state.form_data.get('topic', 'Not set')}")
            st.write(f"**Duration:** {st.session_state.form_data.get('duration', 0)} min")
            st.write(f"**Participants:** {st.session_state.form_data.get('num_participants', 0)}")
            st.write(f"**Languages:** {', '.join(st.session_state.form_data.get('languages', []))}")
        
        st.markdown("---")
        
        # Help section
        st.markdown("### 💡 Tips")
        st.markdown("""
        - Use specific demographics for better results
        - Include cultural context in location
        - Choose AI provider based on languages
        - Review prompt before generating
        """)
    
    # Main content area
    if st.session_state.step == 'form':
        render_form()
    elif st.session_state.step == 'prompt':
        render_prompt_page()
    elif st.session_state.step == 'generating':
        render_generating_page()
    elif st.session_state.step == 'result':
        render_result_page()

if __name__ == "__main__":
    main()