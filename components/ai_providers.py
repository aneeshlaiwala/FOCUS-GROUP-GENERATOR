"""
AI Provider integrations for the Focus Group Generator
"""

import streamlit as st
import openai
import anthropic
import google.generativeai as genai
import cohere
from mistralai.client import MistralClient
from mistralai.models.chat_completion import ChatMessage
import time
import json

class AIProviderManager:
    """Manages all AI provider integrations and handles transcript generation"""
    
    def __init__(self):
        self.providers = {}
        self.rate_limits = {
            'openai': {'requests_per_minute': 3500, 'tokens_per_minute': 90000},
            'anthropic': {'requests_per_minute': 5000, 'tokens_per_minute': 100000},
            'google': {'requests_per_minute': 60, 'tokens_per_minute': 32000},
            'cohere': {'requests_per_minute': 1000, 'tokens_per_minute': 40000},
            'mistral': {'requests_per_minute': 1000, 'tokens_per_minute': 30000}
        }
    
    def initialize_provider(self, provider_name, api_key, model):
        """Initialize a specific AI provider with API key"""
        try:
            if provider_name == 'openai':
                client = openai.OpenAI(api_key=api_key)
                self.providers[provider_name] = {
                    'client': client,
                    'model': model,
                    'type': 'openai'
                }
                
            elif provider_name == 'anthropic':
                client = anthropic.Anthropic(api_key=api_key)
                self.providers[provider_name] = {
                    'client': client,
                    'model': model,
                    'type': 'anthropic'
                }
                
            elif provider_name == 'google':
                genai.configure(api_key=api_key)
                model_obj = genai.GenerativeModel(model)
                self.providers[provider_name] = {
                    'client': model_obj,
                    'model': model,
                    'type': 'google'
                }
                
            elif provider_name == 'cohere':
                client = cohere.Client(api_key=api_key)
                self.providers[provider_name] = {
                    'client': client,
                    'model': model,
                    'type': 'cohere'
                }
                
            elif provider_name == 'mistral':
                client = MistralClient(api_key=api_key)
                self.providers[provider_name] = {
                    'client': client,
                    'model': model,
                    'type': 'mistral'
                }
                
            return True
        except Exception as e:
            st.error(f"Error initializing {provider_name}: {str(e)}")
            return False
    
    def generate_transcript(self, provider_name, prompt, form_data):
        """Generate transcript using the selected AI provider"""
        if provider_name not in self.providers:
            st.error(f"Provider {provider_name} not initialized")
            return None
        
        provider = self.providers[provider_name]
        client = provider['client']
        model = provider['model']
        provider_type = provider['type']
        
        try:
            if provider_type == 'openai':
                response = client.chat.completions.create(
                    model=model,
                    messages=[{"role": "user", "content": prompt}],
                    max_tokens=calculate_word_count(form_data['duration']) * 1.5,  # Approx tokens
                    temperature=0.7
                )
                return response.choices[0].message.content
            
            elif provider_type == 'anthropic':
                response = client.messages.create(
                    model=model,
                    max_tokens=calculate_word_count(form_data['duration']) * 1.5,
                    temperature=0.7,
                    messages=[{"role": "user", "content": prompt}]
                )
                return response.content[0].text
            
            elif provider_type == 'google':
                response = client.generate_content(prompt)
                return response.text
            
            elif provider_type == 'cohere':
                response = client.generate(
                    model=model,
                    prompt=prompt,
                    max_tokens=calculate_word_count(form_data['duration']) * 1.5,
                    temperature=0.7
                )
                return response.generations[0].text
            
            elif provider_type == 'mistral':
                response = client.chat(
                    model=model,
                    messages=[ChatMessage(role="user", content=prompt)]
                )
                return response.choices[0].message.content
            
            return None
        except Exception as e:
            st.error(f"Error generating transcript with {provider_name}: {str(e)}")
            return None
