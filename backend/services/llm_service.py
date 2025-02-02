import logging
from PIL import Image
from io import BytesIO
from google.generativeai import GenerativeModel, configure

logger = logging.getLogger(__name__)

class LLMService:
    def __init__(self, config):
        self.config = config
        configure(api_key=config.GCP_VERTEX_AI_API_KEY)
        self.model = GenerativeModel(config.GEMINI_MODEL_NAME) # e.g., 'gemini-2.0-flash-thinking'

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
                    import json
                    analysis_result = json.loads(llm_output_text)
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
