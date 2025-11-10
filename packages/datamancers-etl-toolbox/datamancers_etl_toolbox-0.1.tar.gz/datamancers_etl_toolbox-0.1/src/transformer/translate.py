from google.cloud import translate_v3
import sys
import random
import json
import os
import logging
import time
import asyncio
from tenacity import retry, wait_random_exponential
from datetime import datetime
from typing import Dict, List, Any  # Add this import




class JsonFormatter(logging.Formatter):
    """Custom JSON formatter for logging."""
    def format(self, record):
        log_entry = {
            'timestamp': datetime.utcnow().isoformat(),
            'level': record.levelname,
            'message': json.loads(record.getMessage()),
            'name': record.name,
            'module': record.module,
            'line': record.lineno,
        }
        return json.dumps(log_entry)

class TranslationGenerator():
    def __init__(self, project_id: str, location: str = None,source_language: str = None,target_language: str = None,log_type: str = "file"):
        if log_type not in ["file", "console"]:
            raise ValueError("Invalid log_type. Must be 'file' or 'console'.")
        self.async_client = translate_v3.TranslationServiceAsyncClient()
        self.sync_client = translate_v3.TranslationServiceClient()
        self.project_id = project_id
        self.location = location
        self.source_language = source_language
        self.target_language = target_language
        if self.location is None:
            self.parent = f"projects/{self.project_id}"
        else:
            self.parent = f"projects/{self.project_id}/locations/{self.location}"
        self.log_file = "translation_usage_log.json"  # Specify the log file path
        self.setup_logger(log_type=log_type)

    def setup_logger(self,log_type):
        """Sets up the logger to log to a JSON file."""
        self.logger = logging.getLogger("TranslationLogger")
        self.logger.setLevel(logging.INFO)

        # Create a file handler
        if log_type == "file":
            handler = logging.FileHandler(self.log_file)
        elif log_type == "console":
            handler = logging.StreamHandler()
        handler.setLevel(logging.INFO)

        # Set the custom JSON formatter
        if log_type == "file":
            formatter = JsonFormatter()
        elif log_type == "console":
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)

        # Add the handler to the logger
        self.logger.addHandler(handler)


    @retry(wait=wait_random_exponential(multiplier=1, max=20))
    async def _async_translate(self, text: str, target_language: str, source_language: str = None, output_type: str = "text") -> Dict[str, Any]:  # Add return type
        
        response = await asyncio.to_thread(self.async_client.translate_text, 
            request= translate_v3.TranslateTextRequest(
                parent=self.parent,
                contents=[text],
                target_language_code=target_language if target_language is not None else self.target_language,
                source_language_code=source_language if source_language is not None else self.source_language,
            )
        )
        self.logger.info({"translated_text": response.translations[0].translated_text})  # Log the translated text
        if output_type == "text":
            return response.translations[0].translated_text
        elif output_type == "dict":
            return response.translations[0].to_dict()

    #@retry(wait=wait_random_exponential(multiplier=1, max=5))
    def _sync_translate(self, text: str, target_language: str = None, source_language: str = None, output_type: str = "text") -> Dict[str, Any]:  # Add return type
        response = self.sync_client.translate_text(
            request=translate_v3.TranslateTextRequest(
                parent=self.parent,
                contents=[text],
                target_language_code=target_language if target_language is not None else self.target_language,
                source_language_code=source_language if source_language is not None else self.source_language,
                mime_type="text/plain",
            )
        )
        response_text = response.translations[0].translated_text
          # Log the translated text
        if output_type == "text":
            self.logger.info({"translated_text": response_text})
            return response_text
        elif output_type == "dict":
            try:
                formatted_response_text = response_text.replace('\\','\\\\').replace('"','\\"').replace("'",'"')
                self.logger.info(formatted_response_text)
                response_dict = json.loads(formatted_response_text)
                error_translations = None
                error_reason = None
            except Exception as e:
                response_dict = {}
                error_translations = response_text
                error_reason = e    
            return response_dict, error_translations, error_reason

        
    async def generate_async(self, input_data: List[Dict[str, Any]], target_language: str,source_language: str = "cs",output_type: str = "text") -> List[Dict[str, Any]]:  # Add return type
        """
        Generates translations based on the provided input data.

        Parameters:
        input_data (List[Dict[str, Any]]): A list of dictionaries where each dictionary represents an item to be processed.
            Each dictionary must contain a key 'text' for the text to be translated.

        Returns:
        List[Dict[str, Any]]: A list of dictionaries containing the translated texts.
        """

        get_translations = [self._async_translate(str(item), target_language,source_language,output_type) for item in input_data]
        return await asyncio.gather(*get_translations)
