"""
Transcript Generator for Focus Group Discussions
Handles the core logic for generating realistic focus group transcripts
"""

import streamlit as st
import requests
import json
import time
from datetime import datetime
from .ai_providers import AIProviderManager
from .utils import calculate_word_count

class TranscriptGenerator:
    """Core transcript generation engine"""
    
    def __init__(self):
        self.ai_manager = AIProviderManager()
        self.research_cache = {}
        
    def generate_full_transcript(self, form_data, api_config, generated_prompt):
        """Generate complete focus group transcript"""
        
        # Initialize AI provider
        provider_name = api_config['provider']
        api_key = api_config['api_key']
        model = api_config['model']
        
        success = self.ai_manager.initialize_provider(provider_name, api_key, model)
        if not success:
            raise Exception(f"Failed to initialize {provider_name}")
        
        # Enhance prompt with research data
        enhanced_prompt = self._enhance_prompt_with_research(generated_prompt, form_data)
        
        # Generate transcript
        transcript = self.ai_manager.generate_transcript(
            provider_name, 
            enhanced_prompt, 
            form_data
        )
        
        if not transcript:
            raise Exception("Failed to generate transcript")
        
        # Post-process transcript
        processed_transcript = self._post_process_transcript(transcript, form_data)
        
        return processed_transcript
    
    def _enhance_prompt_with_research(self, base_prompt, form_data):
        """Enhance the prompt with research data about the topic and location"""
        
        topic = form_data.get('topic', '')
        location = form_data.get('location', '')
        languages = form_data.get('languages', ['English'])
        
        # Research topic online (simplified - in production you'd use real web search)
        research_data = self._research_topic(topic, location)
        
        # Get cultural context
        cultural_context = self._get_cultural_context(location, languages)
        
        # Get language-specific patterns
        language_patterns = self._get_language_patterns(languages, location)
        
        enhanced_prompt = f"""{base_prompt}

RESEARCH INSIGHTS:
{research_data}

CULTURAL CONTEXT FOR {location.upper()}:
{cultural_context}

LANGUAGE PATTERNS:
{language_patterns}

ADDITIONAL INSTRUCTIONS:
- Incorporate the research insights naturally into participant responses
- Use cultural references and local knowledge appropriately
- Apply language patterns and dialect markers as specified
- Ensure responses reflect real market conditions and local perspectives
- Include realistic local references (transportation, food, places, etc.)
"""
        
        return enhanced_prompt
    
    def _research_topic(self, topic, location):
        """Research the topic for the specific location (simplified version)"""
        
        # In production, this would use web search APIs
        # For now, we'll provide contextual guidance based on common topics
        
        research_templates = {
            'electric vehicle': {
                'india': """
- India's EV market is growing rapidly with government push for 2030 targets
- Major concerns: charging infrastructure, price, range anxiety
- Local players: Tata Motors, Mahindra, Hero Electric
- Government incentives: FAME II scheme, state subsidies
- Cultural factors: joint family decisions, value for money mindset
                """,
                'france': """
- France has strong EV adoption with extensive charging network
- Government banned ICE sales by 2040
- Popular models: Renault Zoe, Peugeot e-208
- Concerns: battery replacement costs, winter performance
- Cultural factors: environmental consciousness, government trust
                """,
                'usa': """
- Tesla dominance with growing competition from traditional automakers
- State-level incentives vary significantly
- Range anxiety decreasing with better infrastructure
- Cultural factors: truck culture in rural areas, tech adoption in cities
                """
            },
            'food delivery': {
                'india': """
- Dominated by Zomato and Swiggy
- Concerns: food quality, delivery time, hygiene
- Cultural factors: home-cooked food preference, family meal importance
- Local challenges: address accuracy, payment preferences
                """,
                'global': """
- App-based delivery has changed eating habits
- Concerns: delivery fees, food temperature, packaging waste
- Competition from cloud kitchens and direct restaurant apps
                """
            }
        }
        
        # Match topic keywords
        for key in research_templates:
            if key.lower() in topic.lower():
                location_key = location.lower()
                for loc in research_templates[key]:
                    if loc in location_key:
                        return research_templates[key][loc]
                return research_templates[key].get('global', 'No specific research available')
        
        return f"Research topic '{topic}' in context of {location} market conditions and consumer behavior"
    
    def _get_cultural_context(self, location, languages):
        """Get cultural context for the location"""
        
        cultural_contexts = {
            'mumbai': """
- Fast-paced urban lifestyle, time is precious
- Mix of traditional and modern values
- Local references: local trains, traffic, monsoons
- Communication style: direct but respectful
- Food culture: street food, tiffin system
            """,
            'delhi': """
- Political and business hub mentality
- Status-conscious culture
- Local references: metro, pollution, winter/summer extremes
- Communication style: assertive, hierarchical awareness
            """,
            'bangalore': """
- Tech hub with cosmopolitan outlook
- Young professional demographic
- Local references: traffic, pubs, weather
- Communication style: casual, English-mixed
            """,
            'paris': """
- Fashion and culture consciousness
- Quality over quantity mindset
- Local references: metro, arrondissements, café culture
- Communication style: intellectual, debate-oriented
            """,
            'toronto': """
- Multicultural and polite communication
- Winter weather impacts
- Local references: TTC, neighborhoods, hockey
- Communication style: inclusive, apologetic
            """,
            'new york': """
- Fast-paced, competitive environment
- Diverse borough identities
- Local references: subway, boroughs, seasons
- Communication style: direct, time-conscious
            """
        }
        
        location_key = location.lower()
        for city in cultural_contexts:
            if city in location_key:
                return cultural_contexts[city]
        
        # Default cultural guidance
        return f"Consider local cultural norms, communication styles, and references relevant to {location}"
    
    def _get_language_patterns(self, languages, location):
        """Get language-specific speech patterns and dialect markers"""
        
        patterns = {
            'hinglish': """
- Mix English and Hindi naturally: "I think it's accha", "Cost is too much yaar"
- Use Indian English patterns: "I am doing", "good name", "what is your good name"
- Include fillers: "na", "yaar", "arre", "bas"
- Common phrases: "time pass", "tension mat lo", "scene kya hai"
            """,
            'hindi': """
- Use Devanagari transliterations when appropriate
- Include respectful forms: "aap", "ji"
- Regional variations based on location
- Natural Hindi sentence structures
            """,
            'french': """
- Include "euh", "ben", "alors" as fillers
- Use formal/informal variations appropriately
- Canadian French differences if Quebec location
- Natural French interruption patterns
            """,
            'english': {
                'india': """
- Indian English patterns: "I am having", "good name"
- Local accent markers: "w" sounds, rhythm patterns
- Mix of formal and casual based on education level
                """,
                'uk': """
- British expressions: "brilliant", "quite", "rather"
- Regional accents if specified
- Understatement and politeness patterns
                """,
                'usa': """
- American casual speech: "like", "you know", "totally"
- Regional variations if location specified
- Direct communication style
                """,
                'canada': """
- Canadian markers: "eh", "about" pronunciation
- Polite communication patterns
- Multicultural influences
                """
            }
        }
        
        result = []
        location_lower = location.lower()
        
        for lang in languages:
            lang_lower = lang.lower()
            if lang_lower in patterns:
                if isinstance(patterns[lang_lower], dict):
                    # Handle English with regional variations
                    for region in patterns[lang_lower]:
                        if region in location_lower:
                            result.append(f"{lang}: {patterns[lang_lower][region]}")
                            break
                    else:
                        result.append(f"{lang}: Standard {lang} patterns")
                else:
                    result.append(f"{lang}: {patterns[lang_lower]}")
            else:
                result.append(f"{lang}: Use natural {lang} speech patterns with local dialect variations")
        
        return "\n".join(result)
    
    def _post_process_transcript(self, transcript, form_data):
        """Post-process the generated transcript for quality and consistency"""
        
        # Add header information
        header = self._generate_transcript_header(form_data)
        
        # Clean up formatting
        cleaned_transcript = self._clean_transcript_formatting(transcript)
        
        # Add timestamps if missing
        timestamped_transcript = self._add_timestamps(cleaned_transcript, form_data['duration'])
        
        # Validate word count
        final_transcript = self._adjust_word_count(timestamped_transcript, form_data)
        
        return header + "\n\n" + final_transcript
    
    def _generate_transcript_header(self, form_data):
        """Generate transcript header with metadata"""
        
        current_date = datetime.now().strftime("%B %d, %Y")
        estimated_words = calculate_word_count(form_data['duration'])
        
        header = f"""FOCUS GROUP DISCUSSION TRANSCRIPT

Study Information:
- Topic: {form_data['topic']}
- Date: {current_date}
- Duration: {form_data['duration']} minutes
- Location: {form_data['location']}
- Type: {form_data['discussion_type'].upper()}
- Languages: {', '.join(form_data['languages'])}

Participant Demographics:
- Total Participants: {form_data['num_participants']}
- Gender Distribution: {form_data['male_count']}M, {form_data['female_count']}F, {form_data['non_binary_count']}NB
- Age Range: {form_data['age_range']}
- Profile: {form_data['demographics']}

Study Objective:
{form_data['objective']}

Expected Word Count: ~{estimated_words:,} words
Transcript Status: Generated using AI simulation

{'='*80}"""
        
        return header
    
    def _clean_transcript_formatting(self, transcript):
        """Clean up transcript formatting"""
        
        lines = transcript.split('\n')
        cleaned_lines = []
        
        for line in lines:
            line = line.strip()
            if not line:
                cleaned_lines.append('')
                continue
                
            # Standardize speaker identification
            if line.startswith('[') and ']' in line:
                # Timestamp line
                cleaned_lines.append(line)
            elif ':' in line and any(marker in line.upper() for marker in ['MODERATOR', 'P1', 'P2', 'P3', 'P4', 'P5', 'P6', 'P7', 'P8', 'PARTICIPANT']):
                # Speaker line
                cleaned_lines.append(line)
            else:
                # Regular content
                cleaned_lines.append(line)
        
        return '\n'.join(cleaned_lines)
    
    def _add_timestamps(self, transcript, duration):
        """Add or fix timestamps in transcript"""
        
        lines = transcript.split('\n')
        timestamped_lines = []
        current_time = 0
        time_increment = max(1, duration // 20)  # Roughly 20 timestamps throughout
        
        for line in lines:
            if line.strip().startswith('[') and ']' in line and any(char.isdigit() for char in line):
                # Already has timestamp
                timestamped_lines.append(line)
            elif ':' in line and any(marker in line.upper() for marker in ['MODERATOR', 'P1', 'P2', 'P3', 'P4', 'P5', 'P6', 'P7', 'P8']):
                # Speaker line - add timestamp occasionally
                if current_time == 0 or len([l for l in timestamped_lines if l.startswith('[')]) < current_time // time_increment:
                    minutes = current_time // 60
                    seconds = current_time % 60
                    timestamp = f"[{minutes:02d}:{seconds:02d}] "
                    timestamped_lines.append(timestamp + line)
                    current_time += time_increment
                else:
                    timestamped_lines.append(line)
            else:
                timestamped_lines.append(line)
        
        return '\n'.join(timestamped_lines)
    
    def _adjust_word_count(self, transcript, form_data):
        """Adjust transcript to match expected word count"""
        
        expected_words = calculate_word_count(form_data['duration'])
        actual_words = len(transcript.split())
        
        # If significantly different, add note
        word_ratio = actual_words / expected_words if expected_words > 0 else 1
        
        if word_ratio < 0.8:
            transcript += f"\n\n[Note: Transcript may be shorter than expected. Actual words: ~{actual_words:,}, Expected: ~{expected_words:,}]"
        elif word_ratio > 1.2:
            transcript += f"\n\n[Note: Transcript may be longer than expected. Actual words: ~{actual_words:,}, Expected: ~{expected_words:,}]"
        
        return transcript
    
    def validate_transcript_quality(self, transcript, form_data):
        """Validate the quality of generated transcript"""
        
        quality_checks = {
            'has_moderator': False,
            'has_participants': False,
            'has_timestamps': False,
            'has_opening': False,
            'has_closing': False,
            'appropriate_length': False,
            'natural_flow': False,
            'cultural_references': False
        }
        
        lines = transcript.split('\n')
        word_count = len(transcript.split())
        expected_words = calculate_word_count(form_data['duration'])
        
        # Check for moderator presence
        moderator_lines = [l for l in lines if 'MODERATOR' in l.upper()]
        quality_checks['has_moderator'] = len(moderator_lines) > 0
        
        # Check for participants
        participant_lines = [l for l in lines if any(p in l.upper() for p in ['P1', 'P2', 'P3', 'PARTICIPANT'])]
        quality_checks['has_participants'] = len(participant_lines) > 0
        
        # Check for timestamps
        timestamp_lines = [l for l in lines if l.strip().startswith('[') and ']' in l and any(c.isdigit() for c in l)]
        quality_checks['has_timestamps'] = len(timestamp_lines) > 2
        
        # Check for opening and closing
        transcript_lower = transcript.lower()
        opening_keywords = ['welcome', 'introduction', 'begin', 'start', 'good morning', 'good evening']
        closing_keywords = ['thank you', 'conclude', 'wrap up', 'final thoughts', 'end']
        
        quality_checks['has_opening'] = any(keyword in transcript_lower[:500] for keyword in opening_keywords)
        quality_checks['has_closing'] = any(keyword in transcript_lower[-500:] for keyword in closing_keywords)
        
        # Check appropriate length (within 30% of expected)
        quality_checks['appropriate_length'] = 0.7 <= (word_count / expected_words) <= 1.3
        
        # Check for natural flow indicators
        natural_indicators = ['umm', 'uh', 'you know', 'like', 'actually', 'i think', 'well']
        quality_checks['natural_flow'] = any(indicator in transcript_lower for indicator in natural_indicators)
        
        # Check for cultural references (simplified)
        location = form_data.get('location', '').lower()
        if 'india' in location or 'mumbai' in location or 'delhi' in location:
            cultural_words = ['yaar', 'na', 'arre', 'bas', 'tension', 'time pass']
            quality_checks['cultural_references'] = any(word in transcript_lower for word in cultural_words)
        else:
            quality_checks['cultural_references'] = True  # Assume present for other locations
        
        # Calculate quality score
        passed_checks = sum(quality_checks.values())
        total_checks = len(quality_checks)
        quality_score = passed_checks / total_checks
        
        return {
            'quality_score': quality_score,
            'passed_checks': passed_checks,
            'total_checks': total_checks,
            'checks': quality_checks,
            'word_count': word_count,
            'expected_words': expected_words,
            'recommendations': self._get_quality_recommendations(quality_checks)
        }
    
    def _get_quality_recommendations(self, quality_checks):
        """Get recommendations for improving transcript quality"""
        
        recommendations = []
        
        if not quality_checks['has_moderator']:
            recommendations.append("Add moderator dialogue to guide the discussion")
        
        if not quality_checks['has_participants']:
            recommendations.append("Include more participant responses and interactions")
        
        if not quality_checks['has_timestamps']:
            recommendations.append("Add timestamps to show discussion progression")
        
        if not quality_checks['has_opening']:
            recommendations.append("Include a proper opening with introductions and ground rules")
        
        if not quality_checks['has_closing']:
            recommendations.append("Add a closing section with summary and thanks")
        
        if not quality_checks['appropriate_length']:
            recommendations.append("Adjust transcript length to match expected duration")
        
        if not quality_checks['natural_flow']:
            recommendations.append("Add more natural speech patterns and hesitations")
        
        if not quality_checks['cultural_references']:
            recommendations.append("Include more location-specific cultural references")
        
        return recommendations

class PromptTemplateManager:
    """Manages and generates prompts for different scenarios"""
    
    def __init__(self):
        self.base_templates = {
            'standard': self._get_standard_template(),
            'business': self._get_business_template(),
            'consumer': self._get_consumer_template(),
            'healthcare': self._get_healthcare_template(),
            'technology': self._get_technology_template()
        }
    
    def generate_enhanced_prompt(self, form_data, base_prompt=""):
        """Generate an enhanced prompt based on form data and topic analysis"""
        
        topic = form_data.get('topic', '').lower()
        
        # Determine best template based on topic
        template_type = self._classify_topic(topic)
        template = self.base_templates.get(template_type, self.base_templates['standard'])
        
        # Customize template with form data
        customized_prompt = self._customize_template(template, form_data)
        
        # Add base prompt if provided
        if base_prompt:
            customized_prompt = base_prompt + "\n\n" + customized_prompt
        
        return customized_prompt
    
    def _classify_topic(self, topic):
        """Classify topic to determine appropriate template"""
        
        business_keywords = ['market', 'business', 'strategy', 'sales', 'revenue', 'b2b']
        consumer_keywords = ['consumer', 'customer', 'shopping', 'purchase', 'brand', 'product']
        healthcare_keywords = ['health', 'medical', 'hospital', 'doctor', 'patient', 'wellness']
        technology_keywords = ['technology', 'app', 'software', 'digital', 'ai', 'tech', 'platform']
        
        if any(keyword in topic for keyword in business_keywords):
            return 'business'
        elif any(keyword in topic for keyword in consumer_keywords):
            return 'consumer'
        elif any(keyword in topic for keyword in healthcare_keywords):
            return 'healthcare'
        elif any(keyword in topic for keyword in technology_keywords):
            return 'technology'
        else:
            return 'standard'
    
    def _get_standard_template(self):
        return """
FOCUS GROUP STRUCTURE GUIDELINES:

1. OPENING PHASE (15% of discussion):
   - Warm welcome and moderator introduction
   - Participant introductions (name, brief background)
   - Explanation of process and confidentiality
   - Recording consent
   - Ground rules establishment

2. WARM-UP PHASE (10% of discussion):
   - Icebreaker questions related to topic
   - General opinions and initial reactions
   - Build comfort and rapport

3. CORE DISCUSSION PHASE (65% of discussion):
   - Systematic exploration of key research questions
   - Deep probing with follow-up questions
   - Encourage different perspectives
   - Manage group dynamics
   - Explore underlying motivations

4. CLOSING PHASE (10% of discussion):
   - Summary of key themes
   - Final thoughts and additional comments
   - Thank participants
   - Next steps (if any)

MODERATOR TECHNIQUES:
- Use open-ended questions
- Probe with "Can you tell me more about that?"
- Encourage quiet participants: "Sarah, what's your take on this?"
- Manage dominant speakers tactfully
- Maintain neutrality
- Use active listening techniques
        """
    
    def _get_business_template(self):
        return self._get_standard_template() + """

BUSINESS FOCUS GROUP SPECIFICS:
- Explore decision-making processes
- Understand ROI and cost considerations
- Investigate stakeholder influences
- Discuss implementation challenges
- Explore competitive landscape awareness
- Focus on practical business implications
        """
    
    def _get_consumer_template(self):
        return self._get_standard_template() + """

CONSUMER FOCUS GROUP SPECIFICS:
- Explore emotional connections to products/brands
- Understand purchase journey and touchpoints
- Investigate lifestyle and value influences
- Discuss word-of-mouth and social influences
- Explore unmet needs and pain points
- Focus on user experience and satisfaction
        """
    
    def _get_healthcare_template(self):
        return self._get_standard_template() + """

HEALTHCARE FOCUS GROUP SPECIFICS:
- Handle sensitive topics with care
- Explore trust and credibility factors
- Understand patient/provider relationships
- Investigate accessibility and convenience
- Discuss privacy and security concerns
- Focus on health outcomes and quality of life
- Be mindful of regulatory and ethical considerations
        """
    
    def _get_technology_template(self):
        return self._get_standard_template() + """

TECHNOLOGY FOCUS GROUP SPECIFICS:
- Explore user experience and interface preferences
- Understand adoption barriers and drivers
- Investigate feature priorities and usage patterns
- Discuss privacy and security concerns
- Explore integration with existing workflows
- Focus on learning curves and support needs
- Consider generational and technical skill differences
        """
    
    def _customize_template(self, template, form_data):
        """Customize template with specific form data"""
        
        customizations = f"""
STUDY-SPECIFIC CUSTOMIZATIONS:

Topic: {form_data.get('topic', 'Not specified')}
Objective: {form_data.get('objective', 'Not specified')}
Location: {form_data.get('location', 'Not specified')}
Duration: {form_data.get('duration', 60)} minutes
Participants: {form_data.get('num_participants', 8)} people
Demographics: {form_data.get('demographics', 'Not specified')}
Languages: {', '.join(form_data.get('languages', ['English']))}
Discussion Type: {form_data.get('discussion_type', 'offline')}

PARTICIPANT PERSONAS TO CREATE:
- Generate {form_data.get('num_participants', 8)} distinct participants
- {form_data.get('male_count', 0)} male participants
- {form_data.get('female_count', 0)} female participants  
- {form_data.get('non_binary_count', 0)} non-binary participants
- Age range: {form_data.get('age_range', '25-45')}
- Background: {form_data.get('demographics', 'Mixed demographics')}

CULTURAL AND LINGUISTIC REQUIREMENTS:
- Incorporate {form_data.get('location', 'local')} cultural context
- Use {'/'.join(form_data.get('languages', ['English']))} language patterns
- Include relevant local references and idioms
- Reflect authentic regional communication styles

        """
        
        return template + customizations

# Additional utility functions for transcript generation

def simulate_realistic_timing(base_transcript, duration_minutes):
    """Add realistic timing patterns to transcript"""
    
    lines = base_transcript.split('\n')
    timed_lines = []
    
    # Calculate timing distribution
    total_seconds = duration_minutes * 60
    content_lines = [l for l in lines if l.strip() and not l.startswith('[')]
    
    if not content_lines:
        return base_transcript
    
    # Distribute time across content
    time_per_line = total_seconds / len(content_lines)
    current_time = 0
    
    for line in lines:
        if line.strip() and not line.startswith('['):
            # Add timestamp every few exchanges
            if current_time == 0 or current_time % 300 == 0:  # Every 5 minutes
                minutes = int(current_time // 60)
                seconds = int(current_time % 60)
                timestamp = f"[{minutes:02d}:{seconds:02d}]"
                timed_lines.append(timestamp)
            
            timed_lines.append(line)
            current_time += time_per_line
        else:
            timed_lines.append(line)
    
    return '\n'.join(timed_lines)

def add_natural_speech_patterns(transcript, languages, location):
    """Add natural speech patterns and hesitations"""
    
    # This would be more sophisticated in production
    # For now, we'll add basic patterns
    
    natural_markers = {
        'english': ['um', 'uh', 'you know', 'like', 'actually'],
        'hinglish': ['na', 'yaar', 'arre', 'bas'],
        'french': ['euh', 'ben', 'alors'],
        'spanish': ['pues', 'este', 'bueno']
    }
    
    # Add occasional hesitations and natural speech markers
    # This is a simplified implementation
    return transcript

def generate_participant_names(count, location, gender_distribution):
    """Generate appropriate participant names for the location"""
    
    name_pools = {
        'india': {
            'male': ['Amit', 'Rajesh', 'Vikram', 'Suresh', 'Kiran', 'Arjun', 'Rohit', 'Deepak'],
            'female': ['Priya', 'Sneha', 'Kavita', 'Pooja', 'Meera', 'Sunita', 'Anita', 'Ritu'],
            'surnames': ['Sharma', 'Patel', 'Singh', 'Kumar', 'Gupta', 'Agarwal', 'Jain', 'Shah']
        },
        'france': {
            'male': ['Pierre', 'Jean', 'Michel', 'Alain', 'Philippe', 'Christophe', 'Laurent', 'Éric'],
            'female': ['Marie', 'Françoise', 'Monique', 'Catherine', 'Sylvie', 'Isabelle', 'Martine', 'Nicole'],
            'surnames': ['Martin', 'Bernard', 'Dubois', 'Thomas', 'Robert', 'Petit', 'Durand', 'Leroy']
        },
        'usa': {
            'male': ['John', 'Michael', 'David', 'James', 'Robert', 'William', 'Richard', 'Joseph'],
            'female': ['Mary', 'Patricia', 'Jennifer', 'Linda', 'Elizabeth', 'Barbara', 'Susan', 'Jessica'],
            'surnames': ['Smith', 'Johnson', 'Williams', 'Brown', 'Jones', 'Garcia', 'Miller', 'Davis']
        }
    }
    
    # Determine appropriate name pool based on location
    location_lower = location.lower()
    if 'india' in location_lower:
        pool = name_pools['india']
    elif 'france' in location_lower or 'paris' in location_lower:
        pool = name_pools['france']
    else:
        pool = name_pools['usa']  # Default
    
    # Generate names based on gender distribution
    names = []
    male_count = gender_distribution.get('male', 0)
    female_count = gender_distribution.get('female', 0)
    
    # Add male names
    for i in range(male_count):
        first_name = pool['male'][i % len(pool['male'])]
        surname = pool['surnames'][i % len(pool['surnames'])]
        names.append(f"{first_name} {surname}")
    
    # Add female names
    for i in range(female_count):
        first_name = pool['female'][i % len(pool['female'])]
        surname = pool['surnames'][(i + male_count) % len(pool['surnames'])]
        names.append(f"{first_name} {surname}")
    
    return names[:count]