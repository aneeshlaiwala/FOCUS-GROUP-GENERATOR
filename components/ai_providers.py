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
                self.providers
