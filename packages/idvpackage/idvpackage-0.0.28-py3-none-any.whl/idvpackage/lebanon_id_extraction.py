# import json
# import re
# import time
# from typing import Any, Dict
# import openai
# from idvpackage.common import eastern_arabic_to_english, english_to_eastern_arabic
# from deep_translator import GoogleTranslator
# from datetime import date
# from deep_translator import GoogleTranslator
# import logging
from datetime import date


def is_valid_past_date(date_str: str) -> bool:
    TODAY = date.today()

    # Must be a string in the format dd/mm/yyyy
    if not isinstance(date_str, str):
        return False

    try:
        parts = date_str.split("/")
        if len(parts) != 3:
            return False

        day, month, year = map(int, parts)
    except (ValueError, TypeError):
        return False

    # Rule 1: year > 1900
    if year <= 1900:
        return False

    # Rule 2: month 1..12
    if month < 1 or month > 12:
        return False

    # Basic month -> max day mapping; February handled with leap-year rule
    if month in (1, 3, 5, 7, 8, 10, 12):
        max_day = 31
    elif month in (4, 6, 9, 11):
        max_day = 30
    elif month == 2:
        # leap year?
        is_leap = (year % 4 == 0 and (year % 100 != 0 or year % 400 == 0))
        max_day = 29 if is_leap else 28
    else:
        return False  # unreachable but safe

    if day < 1 or day > max_day:
        return False

    # Now construct date and ensure it's strictly in the past (before TODAY)
    try:
        candidate = date(year, month, day)
    except ValueError:
        return False

    return candidate <= TODAY

# def extract_id_numbers(raw_data):
#     match = re.search(r'[\d٠١٢٣٤٥٦٧٨٩]{7,12}', raw_data)
    
#     if match:
#         id_number_ar = match.group(0)
#         id_number_ar_padded = id_number_ar.zfill(12).replace("0", "٠")
#         id_number_ar_padded = english_to_eastern_arabic(id_number_ar_padded)
#         id_number_en_padded = eastern_arabic_to_english(id_number_ar_padded)
#         return id_number_ar_padded, id_number_en_padded
#     else:
#         return "", ""

# def make_api_request_with_retries(prompt: str, max_retries: int = 3, delay_seconds: float = 2) -> Dict:
#     """
#     Helper function to make API requests with retry logic using OpenAI
#     """
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
#             logging.info(f"OpenAI successfully prompted.{response.choices[0].message.content} ")
#             result = response.choices[0].message.content

#             try:
#                 return json.loads(result)
#             except json.JSONDecodeError:
#                 try:
#                     json_match = re.search(r'```(json|python|plaintext)?\s*(.*?)\s*```|\s*({.*?})', result, re.DOTALL)
#                     if json_match:
#                         json_str = json_match.group(2) or json_match.group(3)
#                         try:
#                             return json.loads(json_str)
#                         except:
#                             return eval(json_str.replace("'", '"'))
#                 except:
#                     pass

#             return json.loads(result)

#         except Exception as e:
#             print(f"Error during API request (attempt {attempt + 1} of {max_retries}): {str(e)}")
#             if attempt < max_retries - 1:
#                 time.sleep(delay_seconds)
#             else:
#                 raise Exception(f"Max retries exceeded. Last error: {str(e)}")


# def lebanon_front_id_extraction(raw_data: str) -> Dict:
#     """
#     Extract front ID data with retry logic
#     """
#     try:
#         prompt = f"From the attached text, please extract the data in a structured format, the response should be a dictionary, having first_name(it can be 1 word or more, please extract accurately), father_name, mother_name, last_name, id_number, dob, place_of_birth, name(full name). Note: If there are more than 1 word for father_name or mother_name, you should pick it smartly, but make sure that it makes sense, don't pick random words for name. Note that the id_number should always be 12 digits, if the length is less than 12 then append 0 in the start for id_number_en and same way for id_number_ar. The extracted details should be in arabic and a transliterated version as well having key_name_en, including id_number, dob(dd/mm/yyyy), names, etc.. the structure should be 'first_name_ar', 'first_name_en', id_number_ar, id_number_en, dob_ar, dob_en, place_of_birth_ar, place_of_birth_en, etc. Make sure that the response should only contain a dictionary, and nothing else. Here's the text for your task: {raw_data}"

#         front_data = make_api_request_with_retries(prompt)

#         if front_data:
#             if front_data.get('place_of_birth_ar', ''):
#                 front_data['place_of_birth'] = front_data.pop('place_of_birth_ar', '')
#             if front_data.get('first_name_ar', ''):
#                 front_data['first_name'] = front_data.pop('first_name_ar', '')
#             if front_data.get('last_name_ar', ''):
#                 front_data['last_name'] = front_data.pop('last_name_ar', '')
#             if front_data.get('father_name_ar', ''):
#                 front_data['father_name'] = front_data.pop('father_name_ar', '')
#             if front_data.get('name_ar', ''):
#                 front_data['name'] = front_data.pop('name_ar', '')
#             if front_data.get('mother_name_ar', ''):
#                 front_data['mother_name'] = front_data.pop('mother_name_ar', '')
#             if front_data.get('id_number_ar', ''):
#                 front_data['id_number'] = eastern_arabic_to_english(front_data.get('id_number_ar', ''))
#                 front_data.pop('id_number_en', '')
#             if front_data.get('dob_en', ''):
#                 front_data['dob'] = front_data.pop('dob_en', '')

#             try:
#                 id_number_ar, id_number_en = extract_id_numbers(raw_data)
#                 if id_number_ar and id_number_en:
#                     if id_number_en != '000000000000':
#                         front_data['id_number_ar'] = id_number_ar
#                         front_data['id_number'] = id_number_en
#             except Exception:
#                 pass

#             if front_data.get('id_number', ''):
#                 if front_data['id_number'] == '000000000000':
#                     front_data['id_number'] = ''
#                     front_data['id_number_ar'] = ''

#     except Exception as e:
#         print(f"Error in processing the extracted data: {e}")
#         front_data = {}

#     return front_data


# def extract_gender_normalized(extracted_text):
#     gender_ar, gender = '', ''
    
#     if re.search(r'ذكر', extracted_text) or re.search(r'ذکر', extracted_text):
#         gender_ar = 'ذكر'
#         gender = 'MALE'

#     elif re.search(r'انثى', extracted_text) or re.search(r'أنثى', extracted_text) or re.search(r'انتی', extracted_text) or re.search(r'انٹی', extracted_text):
#         gender_ar = 'انثى'
#         gender = 'FEMALE'
    
#     return gender_ar, gender


# def lebanon_back_id_extraction(raw_data: str) -> Dict:
#     """
#     Extract back ID data with retry logic
#     """
#     try:
#         prompt = f"From the attached text, please extract the data in a structured format, the response should be a dictionary, having Gender(MALE, FEMALE if no information then null), Marital Status(single, married, widow, if no information then null), Date of Issue, Record Number, Village, Governorate, District. The extracted details should be in arabic and a transliterated version as well having key_name_en, including gender, marital_status, village, etc.. the structure should be 'marital_status_ar', 'marital_status_en', issue_date(dd/mm/yyyy), issue_date_ar(dd/mm/yyyy), governorate_ar, governorate_en, district_ar, district_en, etc. Make sure that the response should only contain a dictionary, and nothing else. Here's the text for your task: {raw_data}"

#         back_data = make_api_request_with_retries(prompt)

#         if back_data:
#             if back_data.get('marital_status_ar', ''):
#                 back_data['marital_status'] = back_data.pop('marital_status_ar', '')

#             if back_data.get('gender_en', ''):
#                 if back_data['gender_en'] in ['MALE', 'FEMALE']:
#                     back_data['gender'] = back_data.pop('gender_en', '')

#             if not back_data.get('gender_en', '') and back_data.get('gender', ''):
#                 back_data['gender'] = back_data.pop('gender', '')

#             if back_data.get('record_number', '') and not back_data.get('record_number_en', ''):
#                 back_data['card_number_ar'] = back_data.get('record_number', '')
#                 back_data['card_number'] = eastern_arabic_to_english(back_data.get('record_number', ''))

#             if back_data.get('record_number_en', ''):
#                 back_data['card_number'] = back_data.pop('record_number_en', '')

#             if back_data.get('record_number_ar', ''):
#                 back_data['card_number_ar'] = back_data.pop('record_number_ar', '')

#             if not back_data.get('gender', ''):
#                 gender_pattern = r"(?:الجنس|Gender)\s*:\s*([\w]+)"
#                 gender_match = re.search(gender_pattern, raw_data, re.IGNORECASE)

#                 gender_ar, gender, back_data['gender'], back_data['gender_ar'] = '', '', '', ''
#                 if gender_match:
#                     gender_ar = gender_match.group(1)
#                     gender = GoogleTranslator(dest = 'en').translate(gender_ar)
#                     if gender.lower() == 'male':
#                         gender = 'MALE'
#                     elif gender.lower() == 'female' or gender.lower() == 'feminine':
#                         gender = 'FEMALE'

#                 if not gender_ar:
#                     gender_ar, gender = extract_gender_normalized(raw_data)

#                 if gender and gender in ['MALE', 'FEMALE']:
#                     back_data['gender'] = gender

#                 if gender_ar and gender in ['MALE', 'FEMALE']:
#                     back_data['gender_ar'] = gender_ar

#             if not back_data.get('issue_date', '') and back_data.get('issue_date_en', ''):
#                 back_data['issue_date'] = back_data.pop('issue_date_en', '')

#             back_data['nationality'], back_data['issuing_country'] = 'LBN', 'LBN'

#     except Exception as e:
#         print(f"Error in processing the extracted data: {e}")
#         back_data = {}
    
#     return back_data



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


PROMPT_FRONT = """
Extract ALL fields from this Lebanon National ID Card **front side** image with high accuracy.

1. ***Extract Names in Arabic***:
        - `first_name`: First name in Arabic exactly as printed
        - `last_name`: Last name in Arabic exactly as printed
        - 'full_name': Full name in Arabic exactly as printed
        - `father_name`: Father's name in Arabic exactly as printed
        - `mother_name`: Mother's name in Arabic exactly as printed

2. ***Transliterate Names to English***:
        - `first_name_en`: Transliterate first name into English
        - `full_name_en`: Transliterate full name into English
        - `father_name_en`: Transliterate father's name into English
        - `mother_name_en`: Transliterate mother's name into English
        - `last_name_en`: Transliterate last name into English
        
3. ***Extract ID Numbers***:
    - `id_number_ar`: Extract exactly 12 digits in Arabic numerals, exactly as printed on the card. Example: ٠٠٠٠١٦٢٣٥٥٧۸
    - `id_number`: Convert the 12-digit Arabic numeral (id_number_ar) into Western/English digits (0–9). Example: id_number_ar = ٠٠٠٠١٦٢٣٥٥٧۸ → id_number = 000016235578

4. ***Extract Place of Birth***:
    - `place_of_birth`: Place of birth in Arabic exactly as printed
    - `place_of_birth_en`: Transliterate place of birth into English
    
5. ***Extract Date of Birth***:
    - `dob_ar`: Extract the date of birth exactly as printed in Arabic numerals
    - `dob`: Convert the Arabic numerals in `dob_ar` into Western/English digits (format: YYYY/MM/DD). Example: dob_ar = ١٩٩٢/١١/٠٥ → dob = 1992/11/05

6. ***Verify header***:
    `header_verified`: Return True if the following texts are present in the image:
        الجمهورية اللبنانية -
وزارة الداخلية  -        otherwhise False

7. ***Verify Civil Status Document***:
    `civil_status_verified`: Return True if any of the texts present in the image are:
        General Directorate, Convergence, Municipalities, Personal Status, statement of individuals, otherwise False

Instructions:
    - Do NOT guess or hallucinate any values. If unclear, return empty string.
    - Only use information visible on the card.
    - Return the result as a single JSON object matching the schema above.
"""

PROMPT_BACK = """
You are an expert in reading Lebanon National ID Cards. Extract the following fields from the **back side** of the ID image.

1. **Extract:**
    -  `gender_ar`: Extract gender in arabic, exactly as printed.
    -  `gender`: Transliterate `gender_ar` into English as either `MALE` or `FEMALE`.
    -  `marital_status`: Extract marital status in Arabic, exactly as printed.
    -  `marital_status_en`: Transliterate `marital_status` into English.
    
2. **Extract dates and card number**:
    - `issue_date_ar`: Extract date of issue in Arabic numerals, exactly as printed, in YYYY/MM/DD format. E.g: '۲۰۰۷/۰۱/۲۵'
    - `issue_date`: Convert `issue_date_ar` into Western/English digits in DD/MM/YYYY format. E.g: '25/01/2007'
    - `card_number_ar`: Extract Arabic Numeral card number exactly as printed
    - `card_number`: Convert `card_number_ar` into Western/English digits (0-9). E.g: '۳۲۳۱' -> 3231 

3. **Extract**:
    - `village_ar`: Extract village in Arabic, exactly as printed.
    - `village_en`: Transliterate `village_ar` into English.
    - `governate_ar`: Extract governate in Arabic, exactly as printed.
    - `governate_en`: Transliterate `governate_ar` into English.
    - `district_ar`: Extract district in Arabic, exactly as printed.
    - `district_en`: Transliterate `district_ar` into English.

    Instructions:
    - Do NOT guess or hallucinate any values. If unclear, return empty string.
    - Only use information visible on the card.
    - Return the result as a single JSON object matching the schema above.

"""


PROMPT_PASSPORT = """
Extract ALL fields from this Lebanon Passport **front side** image with high accuracy.

Return a JSON object with the following fields (use the exact field names):
    - dob: Date of birth exactly as shown on the card, but always return in DD/MM/YYYY format (e.g., '15/06/1990'). If the card shows a different format, convert it to DD/MM/YYYY.
    - expiry_date: Date of expiry exactly as shown on the card, but always return in DD/MM/YYYY format (e.g., '15/06/1990'). If the card shows a different format, convert it to DD/MM/YYYY.
    - issue_date: Date of issue exactly as shown on the card, but always return in DD/MM/YYYY format (e.g., '15/06/1990'). If the card shows a different format, convert it to DD/MM/YYYY.
    - mrz1: First line of the MRZ
    - mrz2: Second line of the MRZ
    - last_name:  name as printed on the card (extract exactly as written) written as name
    - first_name: First name as printed on the card (extract exactly as written)
    - gender: Gender as either M or F (printed as Sex, extract exactly as written), if M output MALE if F output FEMALE
    - father_name: Father's name as printed on the card (extract exactly as written)
    - mother_name: Mother's name as printed on the card (extract exactly as written) extract only english name if both languages are present
    - nationality: Nationality as printed on the card (extract exactly as written and return ISO 3166-1 alpha-3, e.g., LBN)
    - id_number: ID number as printed on the card (exactly 2 letters followed by 7 digits; pad with 0s if fewer digits)
    - place_of_birth: The place of birth in English (printed as Birth Place, extract exactly as written)
    - registry_place_and_number: Extract the registry place (in Arabic, as printed) and the registry number (as printed), and combine them in the format "<Arabic place> <number>"
    - header_verified: Return True if one of the texts present in the image is "Republic of Lebanon" or "Républeue Libanaise", otherwise False.

Instructions:
    - Do NOT guess or hallucinate any values. If unclear, return empty string.
    - Only use information visible on the card.
    - Return the result as a single JSON object matching the schema above.
"""


class LebaneseIDCardFront(BaseModel):
    first_name: str = Field(..., description="First in Arabic, exactly as printed.")
    name: str = Field(..., description="Full name in Arabic, exactly as printed.")
    name_en: str = Field(..., description="Transliterate full name into English.")
    father_name: str = Field(..., description="Father name in Arabic, exactly as printed.")
    mother_name: str = Field(..., description="Mother name in Arabic, exactly as printed.")
    last_name: str = Field(..., description="Last name in Arabic, exactly as printed.")
    first_name_en: str = Field(..., description="Transliterate first name into English.")
    father_name_en: str = Field(..., description="Transliterate father's name into English.")
    mother_name_en: str = Field(..., description="Transliterate mother's name into English.")
    last_name_en: str = Field(..., description="Transliterate last name into English.")
    id_number_ar: str = Field(..., description="12-digit ID number in Arabic numerals, exactly as printed.")
    id_number: str = Field(..., description="Convert 12-digit Arabic numercal ID number into Western/English digits (0-9).")
    dob_ar: str = Field(..., description="Date of Birth in Arabic numerals, exactly as printed.")
    dob: str = Field(..., description="Convert Date of Birth from Arabic numerals to Western/English digits in YYYY/MM/DD format.")
    place_of_birth: str = Field(..., description="Place of Birth in Arabic, exactly as printed.")
    place_of_birth_en: str = Field(..., description="Transliterate Place of Birth into English.")
    header_verified: bool = Field(..., description="Whether the following texts are present in the image: وزارة الداخلية ,الجمهورية اللبنانية")
    civil_status_verified: bool = Field(..., description="Return True if any of the texts present in the image are General Directorate, Convergence, Municipalities, Personal Status, statement of individuals.")

class LebaneseIDCardBack(BaseModel):
    gender_ar: str = Field(..., description="Gender in Arabic, exactly as printed.")
    gender: str = Field(..., description="Transliterate gender into English as Male or Female")
    marital_status: str = Field(..., description="Marital Status in Arabic, exactly as printed.")
    marital_status_en: str = Field(..., description="Transliterate marital status into English.")
    issue_date_ar: str = Field(..., description="Issue Date in Arabic numerals, exactly as printed, in YYYY/MM/DD format.")
    issue_date: str = Field(..., description="Convert Issue Date from Arabic numerals to Western/English digits in DD/MM/YYYY format.")
    card_number_ar: str = Field(..., description="4-digit card number in Arabic numerals, exactly as printed.")
    card_number: str = Field(..., description="Convert 4-digit Arabic numeral card number into Western/English digits (0-9).")
    village_ar: str = Field(..., description="Village in Arabic, exactly as printed.")
    village_en: str = Field(..., description="Transliterate village into English.")
    governate_ar: str = Field(..., description="Governate in Arabic, exactly as printed.")
    governate_en: str = Field(..., description="Transliterate governate into English.")
    district_ar: str = Field(..., description="District in Arabic, exactly as printed.")
    district_en: str = Field(..., description="Transliterate district into English.")



class LebanonPassportFront(BaseModel):
   

    dob: str = Field(...,
        description = "The date of birth (preserve (dd/mm/yyyy) format)",
    )
    expiry_date: str = Field(...,
        description = "The date of expiry  (preserve (dd/mm/yyyy) format)",
    )

    mrz1: str = Field(..., 
        description="First line of the MRZ"
    )

    mrz2: str = Field(..., 
        description="Second line of the MRZ"
    )

    last_name: str = Field(...,
                      description=" name as printed on the card (extract exactly as written on the card)"
                      )
    
    first_name: str = Field(...,
                      description="First name as printed on the card (extract exactly as written on the card)"
                      )
    
    gender: str = Field(...,
        description="Gender as either M or F , (printed as Sex, extract exactly as written on the card)"
    )


    father_name: str = Field(...,
                      description="father name name as printed on the card (extract exactly as written on the card)"
                      )
    
    mother_name: str = Field(...,
                      description= " Mother's full name as printed on the card (look for the label Mother Full Name and extract the name exactly as written in English, Even Arabic is present)"             
                    )

    nationality: str = Field(...,
                      description="Nationality as printed on the card and return ISO 3166-1 alpha-3, e.g., LBN"
    )
    id_number: str = Field(..., min_length=9, max_length=9,
        description = "ID number as printed on the card, extract exactly as written on the card (exactly 2 letters followed by 7 digits; pad with 0s if fewer digits)"
    )
    

    place_of_birth: str = Field(...,
        description = "The place of birth in english(printed as Birth Place, extract exactly as written on the card)",
    )


    issue_date: str = Field(...,
        description = "The date of issue  (preserve (dd/mm/yyyy) format)",
    )
   
    place_of_birth: str = Field(...,
        description = "Place of birth as printed on the card.",
    )


    registry_place_and_number: str = Field(..., 
        description = "extract the registry place (in Arabic, as printed) and the registry number (as printed), and combine them in the format '<Arabic place> <number>'"
    )

    header_verified: bool = Field(
        ...,
        description=" Return True if one of the texts present in the image Republic of Lebanon or Républeue Libanaise ",
    )


    
def process_image(side):

    if side=='front':
        prompt = PROMPT_FRONT
        model = LebaneseIDCardFront

    elif side=='back':
        prompt = PROMPT_BACK
        model = LebaneseIDCardBack

    elif side == "first" or side=='page1':
        prompt = PROMPT_PASSPORT
        model = LebanonPassportFront
        
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



def get_response_from_openai_lbn(image, side, country, openai_key):
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
