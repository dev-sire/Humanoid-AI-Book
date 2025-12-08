"""
Gemini LLM service.

Generates grounded responses using Gemini-2.5-flash with RAG context.
"""

import logging
from typing import List, Dict, Optional
# 1. CHANGE: Import the new Google Generative AI SDK (Gen AI SDK)
from google import genai
from google.genai import types as genai_types
from src.config import settings

logger = logging.getLogger(__name__)


class LLMService:
    """Service for generating responses using Gemini chat models."""

    def __init__(self):
        """Initialize Gemini client."""
        # 2. CHANGE: Initialize the Gemini Client
        # The 'genai.Client' is synchronous by default. We use 'genai.Client().aio' for the async client.
        # It automatically picks up the GEMINI_API_KEY from environment/settings.
        self.client = genai.Client(api_key=settings.gemini_api_key).aio
        self.model = settings.gemini_chat_model

    def _build_system_prompt(self, retrieved_chunks: List[Dict]) -> str:
        # ... (This method remains unchanged, as it only builds a string)
        """
        Build system prompt with retrieved context.

        Args:
            retrieved_chunks: List of retrieved document chunks

        Returns:
            System prompt with context
        """
        context_text = "\n\n".join(
            [
                f"[Source: {chunk['title']} - {chunk['file_path']}]\n{chunk['chunk_text']}"
                for chunk in retrieved_chunks
            ]
        )

        system_prompt = f"""You are a helpful AI assistant for the "Physical AI & Humanoid Robotics" textbook.

Your role is to answer questions based ONLY on the provided book content. Follow these guidelines:

1. GROUNDING: Base all answers strictly on the provided context below. Do not use external knowledge.
2. CITATIONS: Reference specific sources when making claims (e.g., "According to the ROS2 chapter...").
3. SCOPE: If the question is outside the book's scope, politely state: "I don't have information about that in the documentation. I can only answer questions about Physical AI, robotics, ROS2, and related topics covered in this book."
4. CLARITY: Explain technical concepts clearly, suitable for students learning robotics.
5. HONESTY: If the context doesn't contain enough information to answer fully, admit it.

CONTEXT FROM BOOK:
{context_text}

Answer the user's question based on the above context."""

        return system_prompt

    # 3. CHANGE: Update message format for Gemini's Content object
    def _build_conversation_history(
        self, conversation_messages: List[Dict], current_query: str, selected_text: Optional[str]
    ) -> List[genai_types.Content]:
        """
        Build conversation history for LLM context.

        Args:
            conversation_messages: Previous messages in conversation
            current_query: Current user query
            selected_text: Optional selected text from page

        Returns:
            List of Content objects for Gemini API
        """
        messages: List[genai_types.Content] = []

        # Add previous conversation context (last N messages)
        # Note: Gemini uses 'user' and 'model' for roles
        for msg in conversation_messages[-settings.max_conversation_context :]:
            # Convert simple dict to Content object
            messages.append(
                genai_types.Content(
                    role=msg["role"], 
                    parts=[genai_types.Part.from_text(text=msg["content"])]
                )
            )

        # Add current query with selected text if present
        if selected_text:
            query_with_context = f"""Selected text from page: "{selected_text}"

Question: {current_query}"""
            messages.append(
                genai_types.Content(
                    role="user", 
                    parts=[genai_types.Part.from_text(text=query_with_context)]
                )
            )
        else:
            messages.append(
                genai_types.Content(
                    role="user", 
                    parts=[genai_types.Part.from_text(text=current_query)]
                )
            )

        return messages

    async def generate_response(
        self,
        query: str,
        retrieved_chunks: List[Dict],
        conversation_history: List[Dict] = None,
        selected_text: Optional[str] = None,
    ) -> str:
        """
        Generate AI response based on query and retrieved context.
        ...
        """
        try:
            # Build system prompt with context
            system_instruction = self._build_system_prompt(retrieved_chunks)

            # Build conversation history (as list of Content objects)
            conversation_history = conversation_history or []
            contents = self._build_conversation_history(
                conversation_history, query, selected_text
            )

            # 4. CRITICAL CHANGE: Replace client.chat.completions.create with client.models.generate_content
            # System instruction is passed in the config, not in the messages list.
            response = await self.client.models.generate_content(
                model=self.model,
                contents=contents, # The full conversation history + current query
                config=genai_types.GenerateContentConfig(
                    system_instruction=system_instruction, # System prompt goes here
                    temperature=0.7,
                    max_output_tokens=500, # Use max_output_tokens instead of max_tokens
                ),
            )

            # 5. CHANGE: Extract the text from the new response object structure
            answer = response.text
            logger.info(f"Generated response (length: {len(answer)} chars)")
            return answer

        except Exception as e:
            logger.error(f"Failed to generate response: {str(e)}")
            # In a real app, you might check if the error is due to an invalid API key
            # or a content violation (BlockedPromptException).
            raise

    async def check_health(self) -> bool:
        """
        Check if Gemini API is accessible.
        ...
        """
        try:
            # Simple test request using the new method
            # Note: We can reuse the main method for health check as it's cleaner
            response = await self.client.models.generate_content(
                model=self.model,
                contents=[genai_types.Content(
                    role="user", 
                    parts=[genai_types.Part.from_text(text="test")]
                )],
                config=genai_types.GenerateContentConfig(
                    max_output_tokens=5,
                ),
            )
            
            # Check if the response content is non-empty/valid
            return response.text is not None

        except Exception as e:
            logger.error(f"Gemini health check failed: {str(e)}")
            return False