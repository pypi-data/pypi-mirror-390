# from pydantic import BaseModel, Field
# import openai
# import json

# class UAEIDExtractionResult(BaseModel):
#     is_header_verified: bool = Field(..., description="Is it the front side of a UAE ID?")
#     id_number: str = Field(..., description="15-digit UAE ID number")

# def extract_uae_front_id(base64_image: str) -> UAEIDExtractionResult:
#     """
#     Extracts UAE ID front fields using OpenAI's vision model and function calling.
#     Args:
#         openai_api_key (str): OpenAI API key.
#         base64_image (str): Base64-encoded image of the UAE ID front.
#     Returns:
#         UAEIDExtractionResult: Extracted fields in Pydantic model.
#     Raises:
#         Exception: If extraction or parsing fails.
#     """

#     # Define the function schema for OpenAI function calling
#     function_schema = {
#         "name": "UAEIDExtractionResult",
#         "description": "Extracts fields from the front side of a UAE ID card.",
#         "parameters": {
#             "type": "object",
#             "properties": {
#                 "is_header_verified": {
#                     "type": "boolean",
#                     "description": "Is it the front side of a UAE ID?"
#                 },
#                 "id_number": {
#                     "type": "string",
#                     "description": "15-digit UAE ID number"
#                 }
#             },
#             "required": ["is_header_verified", "id_number"]
#         }
#     }
#     prompt = (
#         "You are an expert at extracting information from UAE ID cards. "
#         "Given an image of the front side of a UAE ID, extract the relevant fields. "
#         "If the id_number is not found, set it to an empty string. "
#         "Set is_header_verified to true if the image is the front side of a UAE ID, else false."
#     )
#     try:
#         response = openai.ChatCompletion.create(
#             model="gpt-4o",
#             messages=[
#                 {"role": "system", "content": "You are a helpful assistant."},
#                 {"role": "user", "content": [
#                     {"type": "text", "text": prompt},
#                     {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}}
#                 ]}
#             ],
#             functions=[function_schema],
#             function_call={"name": "UAEIDExtractionResult"},
#             max_tokens=300
#         )
#         message = response.choices[0].message
#         if message.function_call and message.function_call.arguments:
#             args = json.loads(message.function_call.arguments)
#             return UAEIDExtractionResult(**args)
#         else:
#             return {'error':'covered_photo'}
#     except Exception as e:
#         return {'error':'covered_photo'}



import base64
import time
from io import BytesIO
from typing import Optional
import cv2

from openai import OpenAI
from pydantic import BaseModel, Field
import logging


logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    force=True
)


logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    force=True
)



PROMPT_FRONT = """
Extract ALL fields from this UAE National ID **front side** image with high accuracy.

Return a JSON object with the following fields (use the exact field names):

- id_number: The ID number exactly as shown on the card (example: 784-1999-1234567-1 but return without dashes, e.g., 784199912345671)
- header_verified: Return True if one of the texts present in the image is "UNITED ARAB EMIRATES"; otherwise False.

Instructions:
- Do NOT guess or hallucinate any values. If unclear, return empty string.
- Only use information visible on the card.
- Return the result as a single JSON object matching the schema above.
"""


PROMPT_BACK = """
Extract ALL fields from this UAE National ID **back side** image with high accuracy.

Return a JSON object with the following fields (use the exact field names):

- gender_back:  If not present as a separate field, return null. Gender as either M or F. Only extract if it is printed as a separate field on the back side of the card. Do NOT extract from the MRZ.
- date_of_birth_back: If not present as a separate field, return null. Date of birth exactly as shown on the back side of the card preserve DD/MM/YY format. Only extract if it is printed as a separate field. Do NOT extract from the MRZ.
- date_of_expiry_back: If not present as a separate field, return null. Expiry date exactly as shown on the back side of the card preserve DD/MM/YY format. Only extract if it is printed as a separate field. Do NOT extract from the MRZ.
- employer: Employer name as shown in the image (English version; extract exactly as written on the card)
- occupation: Occupation as shown in the image (English version; extract exactly as written on the card)
- card_number: Card number as shown on the card (extract exactly as written, e.g., 119887248)
- issuing_place: Issuing place as shown in the image (extract exactly as written on the card)
- back_header_verified: Return True if one of the texts present in the image is "ILARE" or "IDLARE"; otherwise False.
- mrz1: First line of the MRZ
- mrz2: Second line of the MRZ
- mrz3: Third line of the MRZ
- family_sponsor: Family sponsor name as shown in the image (English version; extract exactly as written on the card)

Instructions:
- Do NOT guess or hallucinate any values. If unclear, return empty string.
- Only use information visible on the card.
- Return the result as a single JSON object matching the schema above.
"""

class UAEFront(BaseModel):

    id_number: str = Field(...,
        description = "The ID number exactly as shown on the card example: 784-1999-1234567-1 but return without dashes (i.e., 784199912345671)",
    )

    
    header_verified: bool = Field(
        ...,
        description=" Return True if one of the texts present in the image UNITED ARAB EMIRATES",
    )

class UAEBack(BaseModel):

    gender_back: str = Field(...,
        description=" If not present as a separate field, return null. Gender as either M or F. Only extract if it is printed as a separate field on the back side of the card. Do NOT extract from the MRZ."
    )

    date_of_birth_back: str = Field(...,
        description = "If not present as a separate field, return null. Date of birth exactly as shown on the back side of the card. Only extract if it is printed as a separate field. Do NOT extract from the MRZ."
    )

    date_of_expiry_back: str = Field(...,
        description = "If not present as a separate field, return null. The expiry date exactly as shown on the back side of the card (preserve original format). Only extract if it is printed as a separate field. Do NOT extract from the MRZ."
    )
   

    employer: str = Field(...,
        description = "Employer name as show in the image English Version(extract exactly as written on the card)",
    )

    occupation: str = Field(...,
        description = "Occupation as show in the image English version(extract exactly as written on the card)",
    )

    card_number: str = Field(...,
        description = "Card number extract exactly as written on the card ex: 119887248"
    )

    issuing_place: str = Field(...,
        description = "Issuing place as show in the image (extract exactly as written on the card)",
    )

    back_header_verified: bool = Field(
        ...,
        description=" Return True if one of the texts present in the image ILARE or  IDARE  ",
    )

    mrz1: str = Field(..., 
        description="First line of the MRZ"
    )

    mrz2: str = Field(..., 
        description="Second line of the MRZ"
    )

    mrz3: str = Field(..., 
        description="Third line of the MRZ"
    )
    
    family_sponsor : str = Field(...,
        description="Family sponsor name as show in the image English Version(extract exactly as written on the card)",
    )




def process_image(side):

    if side == "front":
        prompt = PROMPT_FRONT
        model = UAEFront
    
    elif side == "back":
        prompt =  PROMPT_BACK
        model = UAEBack

    else:
        raise ValueError("Invalid document side specified. please upload front side of passport'.")

    return model, prompt

def get_openai_response(prompt: str, model_type, image: BytesIO, genai_key):
    b64_image = base64.b64encode(image.getvalue()).decode("utf-8")
    for attempt in range(3):
        try:
            client = OpenAI(api_key=genai_key)
            response = client.responses.parse(
                model="gpt-4.1-mini",
                input=[
                    {"role": "system", "content": "You are an expert at extracting information from identity documents."},
                    {"role": "user", "content": [
                        {"type": "input_text", "text": prompt},
                        {"type": "input_image", "image_url": f"data:image/jpeg;base64,{b64_image}", "detail": "low"},
                    ]},
                ],
                text_format=model_type,
            )
            return response.output_parsed
        except Exception as e:
            logging.info(f"[ERROR] Attempt {attempt + 1} failed: {str(e)}")
            time.sleep(2)
    return None

def _image_to_jpeg_bytesio(image) -> BytesIO:
    """
    Accepts: numpy.ndarray (OpenCV BGR), PIL.Image.Image, bytes/bytearray, or io.BytesIO
    Returns: io.BytesIO containing JPEG bytes (ready for get_openai_response)
    """
    import numpy as np

    if isinstance(image, BytesIO):
        image.seek(0)
        return image

    if isinstance(image, (bytes, bytearray)):
        return BytesIO(image)

    try:
        from PIL.Image import Image as _PILImage

        if isinstance(image, _PILImage):
            buf = BytesIO()
            image.convert("RGB").save(buf, format="JPEG", quality=95)
            buf.seek(0)
            return buf
    except Exception:
        pass

    if isinstance(image, np.ndarray):
        success, enc = cv2.imencode(".jpg", image)
        if not success:
            raise ValueError("cv2.imencode failed")
        return BytesIO(enc.tobytes())

    raise TypeError(
        "Unsupported image type. Provide numpy.ndarray, PIL.Image.Image, bytes, or io.BytesIO."
    )

def get_response_from_openai_uae(image, side, country, openai_key):

    logging.info("Processing image for UAE passport extraction OPENAI......")
    logging.info(f" and type: {type(image)}")
    try:
        image = _image_to_jpeg_bytesio(image)
    except Exception as e:
        logging.error(f"Error encoding image: {e}")
        return {"error": "Image encoding failed"}
    try:
        model, prompt = process_image(side)
        logging.info(f"Using model: {model.__name__} and prompt {prompt[:100]}")
    except ValueError as ve:
        logging.error(f"Error: {ve}")
        return {"error": str(ve)}

    try:
        response = get_openai_response(prompt, model, image, openai_key)
    except Exception as e:
        logging.error(f"Error during OpenAI request: {e}")
        return {"error": "OpenAI request failed"}

    response_data = vars(response)
    logging.info(f"Openai response: {response}")
    return response_data