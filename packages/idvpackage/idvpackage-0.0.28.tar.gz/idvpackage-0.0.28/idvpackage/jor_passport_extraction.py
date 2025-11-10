# import google.generativeai as genai
# import re
# from datetime import datetime
# from googletrans import Translator
# import json
# import openai
# import time

# def configure_genai(api_key):
#     genai.configure(api_key=api_key)
#     model = genai.GenerativeModel(model_name="gemini-1.5-flash")
#     return model

# def genai_vision_jor(detected_text, model):
#         result = model.generate_content(
#             [detected_text,"\n\n", "From provided {detected_text} give me all required information in english. full_name, first_name, last_name, mother_name, passport_number, dob(Date of Birth dd/mm/yy format), Place of Birth, gender(M/F), issuing_date(dd/mm/yy format), expiry_date (dd/mm/yy format), Place of Issue, nationality,  and both lines of the MRZ, please give me  just dictionary dont write anything else - full_name, first_name, last_name, mother_name, passport_number, dob, place_of_birth, gender, issuing_date, expiry_date, issuing_place, nationality, mrz1, mrz2. Note that mrz1 is the line that starts with P<JOR and mrz2 is the line that starts with passport number, Also note if you are unable to find the passport number directly then use mrz2 inital words that comes before the symbol '<' as the passport number"]
#         )
#         return  result.text

# def reformat_date(date_str):
#     try:
#         date_obj = datetime.strptime(date_str, '%d-%m-%Y')

#         return date_obj.strftime('%d/%m/%Y')
#     except ValueError:
#         return date_str

# def swap_dates_if_needed(data_dict):
#     try:
#         # Parse the dates
#         issuing_date = datetime.strptime(data_dict['issuing_date'], '%d/%m/%Y')
#         expiry_date = datetime.strptime(data_dict['expiry_date'], '%d/%m/%Y')

#         if issuing_date > expiry_date:
#             data_dict['issuing_date'], data_dict['expiry_date'] = data_dict['expiry_date'], data_dict['issuing_date']
#             print("Dates swapped: Issuing date and expiry date were in the wrong order.")

#     except ValueError as e:
#         print(f"Error parsing dates: {e}")

#     return  data_dict

# def mrz_add(dictionary_image_half):


#     mrz_2 = dictionary_image_half['mrz2']
#     mrz_1 = dictionary_image_half['mrz1']

#     mrz_data_dict = {}


#     pattern_surname = r'P<JOR([^<]+)'
#     match_surname = re.search(pattern_surname, mrz_1)
#     if match_surname:
#         mrz_data_dict['last_name_mrz'] = match_surname.group(1)


#     pattern_given_names = r'<([^<]+)<([^<]+)<([^<]+)<<'
#     match_given_names = re.search(pattern_given_names, mrz_1)
#     if match_given_names:
#         mrz_data_dict['first_name_mrz'] = match_given_names.group(1)
#         mrz_data_dict['middle_name_1'] = match_given_names.group(2)
#         mrz_data_dict['middle_name_2'] = match_given_names.group(3)


#     pattern_passport = r'^([A-Z0-9]+)<'
#     match_passport = re.search(pattern_passport, mrz_2)
#     if match_passport:
#         passport_number = match_passport.group(1)
#         mrz_data_dict['passport_number'] = passport_number


#     pattern_nationality = r'<.[A-Z]{3}'

#     match_nationality = re.search(pattern_nationality, mrz_2)
#     if match_nationality:
#         nationality = match_nationality.group(0)[2:]
#         mrz_data_dict['nationality'] = nationality


#     pattern_birth_date = r'\d{7}<([0-9]{6})'
#     match_birth_date = re.search(pattern_birth_date, mrz_2)
#     if match_birth_date:
#         birth_date_raw = match_birth_date.group(1)
#         year_prefix = '19' if int(birth_date_raw[:2]) > 23 else '20'
#         birth_date = f"{birth_date_raw[4:]}/{birth_date_raw[2:4]}/{year_prefix}{birth_date_raw[:2]}"
#         mrz_data_dict['dob'] = birth_date


#     pattern_gender = r'([MF])'
#     match_gender = re.search(pattern_gender, mrz_2)
#     if match_gender:
#         gender = match_gender.group(1)
#         mrz_data_dict['gender'] = gender


#     pattern_expiry_date = r'[MF](\d{6})'
#     match_expiry_date = re.search(pattern_expiry_date, mrz_2)
#     if match_expiry_date:
#         expiry_date_raw = match_expiry_date.group(1)
#         year_prefix = '19' if int(expiry_date_raw[:2]) > 50 else '20'
#         expiry_date = f"{expiry_date_raw[4:]}/{expiry_date_raw[2:4]}/{year_prefix}{expiry_date_raw[:2]}"
#         mrz_data_dict['expiry_date'] = expiry_date


#         for key, value in mrz_data_dict.items():
#             if key in dictionary_image_half and dictionary_image_half[key] in ['None', None, 'N/A', '', ' ', 'NaN', 'nan', 'null']:
#                 dictionary_image_half[key] = value
#             elif key not in dictionary_image_half:
#                 dictionary_image_half[key] = value


#         if len(dictionary_image_half['last_name']) > 1:
#             # Substitute last_name with last_name_mrz
#             dictionary_image_half['last_name'] = dictionary_image_half['last_name_mrz']


#     return dictionary_image_half

# def translate_arabic_words(dictionary):
#     translator = Translator()
#     translated_dict = {}
#     for key, value in dictionary.items():
#         if key not in ['mrz1', 'mrz2']:
#             if isinstance(value, str):

#                 detected_lang = translator.detect(value).lang
#                 if detected_lang == 'ar':
#                     translated_text = translator.translate(value, src='ar', dest='en').text
#                     translated_dict[key] = translated_text
#                 else:
#                     translated_dict[key] = value
#             else:
#                 translated_dict[key] = value
#         else:

#             translated_dict[key] = value
#     return translated_dict

# def make_api_request_with_retries(prompt: str, max_retries: int = 3, delay_seconds: float = 2):
#     """
#     Helper function to make API requests with retry logic using OpenAI
#     """
#     start_time = time.time()
#     for attempt in range(max_retries):
#         try:
#             response = openai.ChatCompletion.create(
#                 model="gpt-4o",
#                 temperature=0.4,
#                 max_tokens=2000,
#                 messages=[
#                     {
#                         "role": "user",
#                         "content": prompt
#                     }
#                 ]
#             )
#             result = response.choices[0].message.content

#             try:
#                 api_response = json.loads(result)
#             except json.JSONDecodeError:
#                 try:
#                     json_match = re.search(r'```(json|python|plaintext)?\s*(.*?)\s*```|\s*({.*?})', result, re.DOTALL)
#                     if json_match:
#                         json_str = json_match.group(2) or json_match.group(3)
#                         try:
#                             api_response = json.loads(json_str)
#                         except:
#                             api_response = eval(json_str.replace("'", '"'))
#                     else:
#                         raise json.JSONDecodeError("No JSON found in response", result, 0)
#                 except Exception as e:
#                     print(f"Error parsing response: {str(e)}")
#                     raise

#             # print(f"GenAI request took {time.time() - start_time:.2f} seconds")
#             return api_response

#         except Exception as e:
#             print(f"Error during API request (attempt {attempt + 1} of {max_retries}): {str(e)}")
#             if attempt < max_retries - 1:
#                 time.sleep(delay_seconds)
#             else:
#                 raise Exception(f"Max retries exceeded. Last error: {str(e)}")

# def jordan_passport_extraction(passport_text, api_key):
#     start_time = time.time()
#     try:
#         prompt = f"From provided text, give me all required information in english only. full_name, first_name, last_name, mother_name, passport_number, national_number, dob(Date of Birth dd/mm/yyyy format), Place of Birth, gender(M/F), issuing_date(dd/mm/yyyy format), expiry_date (dd/mm/yyyy format), Place of Issue, nationality, and both lines of the MRZ(mrz1, mrz2). Please give me just dictionary dont write anything else - full_name, first_name, last_name, mother_name, passport_number, national_number, dob, place_of_birth, gender, issuing_date, expiry_date, issuing_place, nationality, mrz1, mrz2. Note that mrz1 is the line that starts with P<JOR and mrz2 is the line that starts with passport number. Also note if you are unable to find the passport number directly then use mrz2 initial words that comes before the symbol '<' as the passport number. If there are any arabic words in mother_name, or place_of_birth, or authority, just keep the english words, do not ever include arabic words in the output. Leave National No. empty if not found. Here's the text: {passport_text}"

#         passport_final_result = make_api_request_with_retries(prompt)

#         if 'national_number' in passport_final_result:
#             passport_final_result['passport_national_number'] = passport_final_result.get('national_number', '')

#         # print(f"\nPassport GenAI result: {passport_final_result}\n")

#         # try:
#         #     passport_final_result = swap_dates_if_needed(passport_final_result)
#         # except Exception as e:
#         #     print(f"Error swapping dates: {e}")

#         # try:
#         #     passport_final_result = translate_arabic_words(passport_final_result)
#         # except Exception as e:
#         #     print(f"Error translating: {e}")

#         if passport_final_result and not passport_final_result.get('passport_number', ''):
#             passport_number_pattern = r"([A-Za-z]\d{8}|[A-Za-z]\d{7}|[A-Za-z]\d{6})"
#             passport_number_match = re.search(passport_number_pattern, passport_text)
#             if passport_number_match:
#                 passport_number = passport_number_match.group(0)

#                 if passport_number:
#                     passport_final_result['passport_number'] = passport_number
#                 else:
#                     passport_number_match = re.search(passport_number_pattern, passport_final_result.get('mrz2', ''))
#                     if passport_number_match:
#                         passport_number = passport_number_match.group(0)
#                         passport_final_result['passport_number'] = passport_number

#         mrz1 = passport_final_result.get('mrz1', '')
#         mrz2 = passport_final_result.get('mrz2', '')
#         if mrz1 and mrz2:
#             passport_final_result['mrz'] = f"{mrz1} {mrz2}"

#         if "gender" in passport_final_result:
#             gender = passport_final_result["gender"].strip().upper()
#             if gender == "F":
#                 passport_final_result["gender"] = "FEMALE"
#             elif gender == "M":
#                 passport_final_result["gender"] = "MALE"

#         if 'gender' in passport_final_result:
#             passport_final_result["gender"] = passport_final_result["gender"].strip().upper()

#         if 'issuing_place' in passport_final_result:
#             passport_final_result['place_of_issue'] = passport_final_result['issuing_place'].strip().upper()

#         if passport_final_result.get('nationality', '') and len(passport_final_result['nationality']) > 3:
#             passport_final_result['nationality'] = 'JOR'

#         if not passport_final_result.get('nationality', ''):
#             passport_final_result['nationality'] = 'JOR'

#         passport_final_result['issuing_country'] = 'JOR'

#         processing_time = time.time() - start_time

#         return passport_final_result

#     except Exception as e:
#         processing_time = time.time() - start_time
#         print(f"Error occurred in passport extraction: {e}")
#         print(f"Failed processing took {processing_time:.2f} seconds")
#         return {}

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
    format="%(asctime)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    force=True,
)


PROMPT_PASSPORT = """
Extract ALL fields from this Jordan Passport **front side** image with high accuracy.

Return a JSON object with the following fields (use the exact field names):

- dob: Date of birth exactly as shown on the card, but always return in DD/MM/YYYY format (e.g., '15/06/1990'). If the card shows a different format, convert it to DD/MM/YYYY.
- date_of_expiry: Date of expiry exactly as shown on the card, but always return in DD/MM/YYYY format (e.g., '15/06/1990'). If the card shows a different format, convert it to DD/MM/YYYY.
- mrz1: First line of the MRZ (extract exactly as written).
- mrz2: Second line of the MRZ (extract exactly as written).
- name: Full name as printed on the card (extract exactly as written).
- first_name: First name as printed on the card (extract exactly as written).
- gender: Gender as either M or F (printed as Sex; output MALE if M, FEMALE if F).
- place_of_issue: Issuing place as printed on the card (extract exactly as written).
- full_name: Full name as printed on the card (extract exactly as written).
- last_name: Last name from the full name (extract exactly as written; if not present, return null).
- mother_name: Mother's full name as printed on the card (look for the label "Mother Full Name" and extract the name exactly as written in English, even if Arabic is present).
- nationality: Nationality as printed on the card and return ISO 3166-1 alpha-3 code (e.g., JOR).
- passport_national_number: National number as printed on the card (extract exactly as written) return empty string if not present.
- passport_number: Passport number as printed on the card (exactly 8 characters)
- issuing_date: Date of issue exactly as shown on the card, always in DD/MM/YYYY format.
- place_of_birth: Place of birth as printed on the card, tagged under Address (extract exactly as written).
- header_verified: Return True if any of these texts are present in the image: "Hashemite Kingdom of Jordan", "Hashemite Kingdom", or "Jordan"; otherwise False.

Instructions:
- Do NOT guess or hallucinate any values. If unclear,return empty string.
- Only use information visible on the card.
- Return the result as a single JSON object matching the schema above.
"""


class JordanPassportFront(BaseModel):
    dob: str = Field(
        ...,
        description="The date of birth (preserve (dd/mm/yyyy) format)",
    )
    expiry_date: str = Field(
        ...,
        description="The date of expiry  (preserve (dd/mm/yyyy) format) tagged as Date if Expiry",
    )

    mrz1: str = Field(..., description="First line of the MRZ")

    mrz2: str = Field(..., description="Second line of the MRZ")

    name: str = Field(
        ...,
        description="Full name as printed on the card (extract exactly as written on the card)",
    )

    first_name: str = Field(
        ...,
        description="First name as printed on the card (extract exactly as written on the card)",
    )

    gender: str = Field(
        ...,
        description="Gender as either M or F , (printed as Sex,  Male if M or Female if F)",
    )

    place_of_issue: str = Field(
        ...,
        description="Issuing place as printed on the card (extract exactly as written on the card)",
    )

    full_name: str = Field(
        ...,
        description="Full name as printed on the card (extract exactly as written on the card)",
    )

    last_name: Optional[str] = Field(
        None,
        description="Last name from the full name",
    )

    mother_name: str = Field(
        ...,
        description=" Mother's full name as printed on the card (look for the label Mother Full Name and extract the name exactly as written in English, Even Arabic is present)",
    )

    nationality: str = Field(
        ...,
        description="Nationality as printed on the card and return ISO 3166-1 alpha-3, e.g., JOR",
    )

    passport_number: str = Field(
        ...,
        min_length=8,
        max_length=8,
        description="ID number as printed on the card, extract exactly as written on the card ",
    )

    passport_national_number: str = Field(
        ...,
        description="National number as printed on the card, extract exactly as written on the card  return empty string if not present",
    )

    issuing_date: str = Field(
        ...,
        description="The date of issue  (preserve (dd/mm/yyyy) format)",
    )

    place_of_birth: str = Field(
        ...,
        description="Place of birth as printed on the card tagged under Address tag, extract exactly as written on the card",
    )

    header_verified: bool = Field(
        ...,
        description=" Return True if one of the texts present in the image Hashemite Kingdom of Jordan or Hashemite Kingdom or Jordan ",
    )


def process_image(side):
    if side == "first" or side == "page1":
        prompt = PROMPT_PASSPORT
        model = JordanPassportFront

    else:
        raise ValueError(
            "Invalid document side specified. please upload front side of passport'."
        )

    return model, prompt


def get_openai_response(prompt: str, model_type, image: BytesIO, genai_key):
    b64_image = base64.b64encode(image.getvalue()).decode("utf-8")
    for attempt in range(3):
        try:
            client = OpenAI(api_key=genai_key)
            response = client.responses.parse(
                model="gpt-4.1-mini",
                input=[
                    {
                        "role": "system",
                        "content": "You are an expert at extracting information from identity documents.",
                    },
                    {
                        "role": "user",
                        "content": [
                            {"type": "input_text", "text": prompt},
                            {
                                "type": "input_image",
                                "image_url": f"data:image/jpeg;base64,{b64_image}",
                                "detail": "low",
                            },
                        ],
                    },
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


def get_response_from_openai_jor(image, side, country, openai_key):
    logging.info("Processing image for Jordan passport extraction OPENAI......")
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
