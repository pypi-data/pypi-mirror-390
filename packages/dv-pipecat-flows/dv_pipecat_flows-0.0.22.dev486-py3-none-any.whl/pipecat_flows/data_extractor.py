#
# Copyright (c) 2024, Daily
#
# SPDX-License-Identifier: BSD 2-Clause License
#
"""Data extraction system for Pipecat Flows.

This module provides functionality to extract and store data at the node level
from either function responses or conversation context, making it available
to downstream nodes through the flow manager's state.
"""

import json
from typing import Any, Dict, List, Optional

from loguru import logger
from pipecat.frames.frames import LLMMessagesAppendFrame
from pipecat.processors.aggregators.llm_context import LLMContext


class DataExtractor:
    """Handles extraction of data from function responses and conversations."""

    def __init__(self):
        """Initialize the data extractor."""
        self._extraction_cache = {}

    async def extract_from_function_response(
        self,
        function_name: str,
        response: Dict[str, Any],
        extraction_fields: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        """Store complete function response for specified fields.

        Args:
            function_name: Name of the function that produced the response.
            response: The complete response from the function.
            extraction_fields: List of extraction field configurations.

        Returns:
            Dictionary mapping field keys to extracted values.
        """
        extracted_data = {}

        for field in extraction_fields:
            if field.get("extraction_type") != "function_response":
                continue

            if field.get("source_function") != function_name:
                continue

            key = field.get("key")
            if not key:
                logger.warning(f"Extraction field missing 'key' for function {function_name}")
                continue

            # Store the complete response
            extracted_data[key] = response
            logger.debug(f"Extracted function response for key '{key}' from {function_name}")

        return extracted_data

    async def extract_from_conversation(
        self,
        context: List[Dict[str, Any]],
        extraction_fields: List[Dict[str, Any]],
        llm_service: Any,
    ) -> Dict[str, Any]:
        """Use LLM to extract data from conversation context.

        Args:
            context: The conversation context (list of messages).
            extraction_fields: List of extraction field configurations.
            llm_service: The LLM service to use for extraction.

        Returns:
            Dictionary mapping field keys to extracted values.
        """
        extracted_data = {}

        # Filter for conversation-type extractions
        conversation_fields = [
            f for f in extraction_fields if f.get("extraction_type") == "conversation"
        ]

        if not conversation_fields:
            return extracted_data

        # Build extraction prompt
        extraction_prompt = self._build_extraction_prompt(context, conversation_fields)

        try:
            # Create a temporary context for extraction
            extraction_messages = [
                {
                    "role": "system",
                    "content": "You are a data extraction assistant. Extract the requested information from the conversation and return it as JSON.",
                },
                {"role": "user", "content": extraction_prompt},
            ]

            # Use LLM to extract data
            # Note: This assumes the LLM service has a method to get completions
            # You may need to adjust based on your LLM service implementation
            response = await self._get_llm_extraction(llm_service, extraction_messages)

            if response:
                try:
                    # Parse the JSON response
                    extracted = json.loads(response)
                    for field in conversation_fields:
                        key = field.get("key")
                        if key and key in extracted:
                            extracted_data[key] = extracted[key]
                            logger.debug(f"Extracted conversation data for key '{key}'")
                except json.JSONDecodeError as e:
                    logger.error(f"Failed to parse LLM extraction response: {e}")
                    # Try to extract raw values as fallback
                    for field in conversation_fields:
                        key = field.get("key")
                        if key:
                            extracted_data[key] = None

        except Exception as e:
            logger.error(f"Error during conversation extraction: {e}")
            # Set all fields to None on error
            for field in conversation_fields:
                key = field.get("key")
                if key:
                    extracted_data[key] = None

        return extracted_data

    def _build_extraction_prompt(
        self, context: List[Dict[str, Any]], fields: List[Dict[str, Any]]
    ) -> str:
        """Build a prompt for LLM extraction.

        Args:
            context: The conversation context.
            fields: Fields to extract.

        Returns:
            The extraction prompt string.
        """
        # Format the conversation
        conversation_text = "\n".join(
            [f"{msg.get('role', 'unknown')}: {msg.get('content', '')}" for msg in context[-10:]]
        )

        # Build field descriptions
        field_descriptions = []
        for field in fields:
            key = field.get("key")
            description = field.get("description", f"Extract {key}")
            field_descriptions.append(f"- {key}: {description}")

        prompt = f"""Given the following conversation:

{conversation_text}

Please extract the following information and return it as a JSON object:
{chr(10).join(field_descriptions)}

Return only valid JSON with the extracted values. If a value cannot be determined, use null.
"""
        return prompt

    async def _get_llm_extraction(
        self, llm_service: Any, messages: List[Dict[str, Any]]
    ) -> Optional[str]:
        """Get extraction response from LLM.

        This is a placeholder that needs to be adapted based on the specific
        LLM service implementation.

        Args:
            llm_service: The LLM service instance.
            messages: Messages to send to the LLM.

        Returns:
            The LLM response as a string, or None if failed.
        """
        try:
            # This implementation depends on your LLM service
            # For OpenAI-style services:
            if hasattr(llm_service, "_client"):
                # Assuming OpenAI-style client
                response = await llm_service._client.chat.completions.create(
                    model=llm_service._model,
                    messages=messages,
                    temperature=0.1,  # Low temperature for consistent extraction
                    response_format={"type": "json_object"},  # Request JSON format
                )
                return response.choices[0].message.content
            else:
                logger.warning("LLM service does not support extraction, returning None")
                return None
        except Exception as e:
            logger.error(f"Error calling LLM for extraction: {e}")
            return None

    async def process_node_extractions(
        self,
        node_name: str,
        extraction_config: List[Dict[str, Any]],
        function_results: Optional[Dict[str, Dict[str, Any]]] = None,
        conversation_context: Optional[List[Dict[str, Any]]] = None,
        llm_service: Optional[Any] = None,
    ) -> Dict[str, Any]:
        """Process all data extractions for a node.

        Args:
            node_name: Name of the current node.
            extraction_config: List of extraction field configurations.
            function_results: Map of function names to their results.
            conversation_context: The conversation context.
            llm_service: The LLM service for conversation extraction.

        Returns:
            Dictionary with all extracted data for the node.
        """
        if not extraction_config:
            return {}

        all_extracted = {}

        # Process function response extractions
        if function_results:
            for func_name, result in function_results.items():
                func_extracted = await self.extract_from_function_response(
                    func_name, result, extraction_config
                )
                all_extracted.update(func_extracted)

        # Process conversation extractions
        if conversation_context and llm_service:
            conv_extracted = await self.extract_from_conversation(
                conversation_context, extraction_config, llm_service
            )
            all_extracted.update(conv_extracted)

        if all_extracted:
            logger.info(
                f"Extracted {len(all_extracted)} data fields for node '{node_name}': {list(all_extracted.keys())}"
            )

        return all_extracted