import logging
from PIL import Image
import re
import json
from io import BytesIO
from google.generativeai import GenerativeModel, configure

logger = logging.getLogger(__name__)

class LLMService:
    def __init__(self, config):
        self.config = config
        configure(api_key=config.get('GCP_VERTEX_AI_API_KEY'))
        self.model = GenerativeModel(config.get('GEMINI_MODEL_NAME')) # e.g., 'gemini-2.0-flash-thinking'

    def parse_gemini_json_response(self, gemini_response_text):
        """Extracts and parses JSON from a Gemini response string."""

        # 1. Remove code block markers (```json and ```)
        cleaned_text = gemini_response_text.replace("```json", "").replace("```", "").strip()

        # 2. Remove any leading/trailing newlines or whitespace
        cleaned_text = cleaned_text.strip()

        # 3. (Optional but Recommended) Use a regular expression for more robust cleaning:
        # This handles cases where there might be other non-JSON content outside the code block.
        match = re.search(r"\{.*\}", cleaned_text, re.DOTALL)  # Find the JSON object
        if match:
            cleaned_text = match.group(0)
        else:
            return None # Or raise an exception, or return an empty dict if no JSON is found.

        try:
            data = json.loads(cleaned_text)
            return data
        except json.JSONDecodeError as e:
            print(f"JSONDecodeError: {e}")
            print(f"Problematic JSON string: {cleaned_text}")  # Print the problematic string for debugging
            return None  # Or raise the exception if you want to stop execution
            
    def analyze_image(self, image_bytes):
        try:
            image = Image.open(BytesIO(image_bytes))
            prompt = '''Describe the objects and scene in this image in detail, and identify any detected objects with bounding boxes if possible. \n
                        Output in JSON format with 'text_description' and 'detected_objects'.
                        'text_description' should be less then 100 words, explaning what the frame contains.
                        'detected_objects' should be a list of max to 10 objects with 'object_type', 'object_color', 'object_descrition').
                        Never return masks or code fencing. Never ask questions. Do not describe the image format, and do not mention colors if you are not sure.
            '''

            response = self.model.generate_content([prompt, image])
            response.resolve() # Resolve futures, handle potential errors.

            if response.parts:
                llm_output_text = response.parts[0].text # Assuming text output is the first part
                # **Important:** You'll need to parse the JSON output from Gemini here.
                # Gemini's output format needs to be reliably parsed. This is a placeholder.
                # Example parsing (adjust based on actual Gemini output):

                try:
                    analysis_result = self.parse_gemini_json_response(llm_output_text)
                    logger.debug(f"LLM Analysis Result: {analysis_result}")
                    return analysis_result
                except json.JSONDecodeError:
                    logger.warning(f"Could not parse JSON from LLM output: {llm_output_text}")
                    return {'text_description': llm_output_text, 'detected_objects': []} # Fallback

            else:
                logger.warning("LLM response had no parts.")
                return {'text_description': 'No description from LLM', 'detected_objects': []}

        except Exception as e:
            logger.error(f"Error analyzing image: {e}", exc_info=True)
            return {'text_description': 'Error during image analysis', 'detected_objects': []}
