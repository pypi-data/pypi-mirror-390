# import re
# import google.generativeai as genai
# from datetime import datetime
# from googletrans import Translator
# import json
# import logging

# def configure_genai(api_key):
#     try:
#         genai.configure(api_key=api_key)
#         model = genai.GenerativeModel(model_name = "gemini-2.0-flash-lite")
#         logging.info("GenAI model configured successfully.")
#         return model
#     except Exception as e:
#         logging.error(f"Error configuring GenAI: {e}")
#         return None

# def genai_vision_pse(detected_text, model):
#     result = model.generate_content(
#         [detected_text, "\n\n", "From provided {detected_text}  give me all required information in english. full_name, first_name, last_name, mother_name, passport_number(only digits, i.e N° or No), id_number, dob(Date of Birth dd/mm/yy format), Place of Birth, gender(M/F), issuing_date(dd/mm/yy format), expiry_date (dd/mm/yy format), Place of Issue, occupation(profession), nationality  and both lines of the MRZ, please give me  just dictionary dont write anything else - full_name, first_name, last_name, mother_name, passport_number, id_number, dob, place_of_birth: gender, issuing_date, expiry_date, issuing_place, occupation, mrz1, mrz2. Note that mrz1 is the line that starts with P and mrz2 is the line that starts with passport number"]
#     )
#     logging.info(f"GenAI Raw Output: {result.text}")    
#     return  result.text

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
#             logging.info("Dates swapped: Issuing date and expiry date were in the wrong order.")

#     except ValueError as e:
#         logging.info(f"Error parsing dates: {e}")

#     return  data_dict

# def mrz_add(mrz_data_dict):
#     mrz_2 = mrz_data_dict['mrz2']
#     mrz_1 = mrz_data_dict['mrz1']

#     # 1. Extract Passport Number
#     try:
#         if 'passport_number' not in mrz_data_dict:
#             pattern_passport = r'^(\d{7})'
#             match_passport = re.search(pattern_passport, mrz_2)
#             if match_passport:
#                 passport_number = match_passport.group(1)
#                 mrz_data_dict['passport_number'] = passport_number
#     except Exception as e:
#         print(f"Error extracting passport number for PSE: {e}")

#     # 2. Extract Nationality
#     try:
#         if 'nationality' not in mrz_data_dict:
#             pattern_nationality = r'<\d([A-Z]{3})'
#             match_nationality = re.search(pattern_nationality, mrz_2)
#             if match_nationality:
#                 nationality = match_nationality.group(1)
#                 mrz_data_dict['nationality'] = nationality
#     except Exception as e:
#         logging.info(f"Error extracting nationality for PSE: {e}")

#     # 3. Extract Date of Birth (DD/MM/YYYY format)
#     try:
#         if 'dob' not in mrz_data_dict:
#             pattern_birth_date = r'\d{7}<\d[A-Z]{3}(\d{6})'
#             match_birth_date = re.search(pattern_birth_date, mrz_2)
#             if match_birth_date:
#                 birth_date_raw = match_birth_date.group(1)
#                 year_prefix = '19' if int(birth_date_raw[:2]) > 23 else '20'
#                 birth_date = f"{birth_date_raw[4:]}/{birth_date_raw[2:4]}/{year_prefix}{birth_date_raw[:2]}"
#                 mrz_data_dict['dob'] = birth_date
#     except Exception as e:
#         logging.info(f"Error extracting date of birth for PSE: {e}")

#     # 4. Extract Gender
#     try:
#         if 'gender' not in mrz_data_dict:
#             pattern_gender = r'[A-Z]{3}\d{6}([MF])'
#             match_gender = re.search(pattern_gender, mrz_2)
#             if match_gender:
#                 gender = match_gender.group(1)
#                 mrz_data_dict['gender'] = gender
#     except Exception as e:
#         print(f"Error extracting gender for PSE: {e}")

#     # 5. Extract Expiration Date (DD/MM/YYYY format)
#     try:
#         if 'expiry_date' not in mrz_data_dict:
#             pattern_expiration_date = r'[MF](\d{6})'
#             match_expiration_date = re.search(pattern_expiration_date, mrz_2)
#             if match_expiration_date:
#                 expiration_date_raw = match_expiration_date.group(1)
#                 year_prefix = '19' if int(expiration_date_raw[:2]) > 50 else '20'
#                 expiration_date = f"{expiration_date_raw[4:]}/{expiration_date_raw[2:4]}/{year_prefix}{expiration_date_raw[:2]}"
#                 mrz_data_dict['expiry_date'] = expiration_date
#     except Exception as e:
#         logging.info(f"Error extracting expiration date for PSE: {e}")

#     # 6. Extract Surname from MRZ_1
#     # Updated to handle multiple variations of MRZ structures.
#     try:
#         if 'last_name' not in mrz_data_dict:
#             pattern_surname = r'P<PSE([A-Z]+)<'
#             match_surname = re.search(pattern_surname, mrz_1)
#             if match_surname:
#                 surname = match_surname.group(1)
#                 mrz_data_dict['last_name'] = surname
#     except  Exception as e:
#         print(f"Error extracting surname for PSE: {e}")

#     # 7. Extract Given Name (First Name) from MRZ_1
#     # Modified pattern to not rely on `<F`, as MRZ_1 structure can vary.
#     try:
#         if 'first_name' not in mrz_data_dict:
#             pattern_given_name = r'<([A-Z]+)<[A-Z]<'
#             match_given_name = re.search(pattern_given_name, mrz_1)
#             if match_given_name:
#                 given_name = match_given_name.group(1)
#                 mrz_data_dict['first_name'] = given_name
#     except Exception as e:
#         print(f"Error extracting first name for PSE: {e}")

#     # 8. If the surname or name isn't filled, use a fallback approach
#     # If MRZ_1 structure varies, you can adjust these patterns.
#     try:
#         if 'last_name' not in mrz_data_dict:
#             # Fallback to capture everything after the country code
#             fallback_pattern_surname = r'P<PSE([A-Z]+)'
#             match_surname = re.search(fallback_pattern_surname, mrz_1)
#             if match_surname:
#                 mrz_data_dict['last_name'] = match_surname.group(1)
#     except Exception as e:
#         print(f"Error extracting surname for PSE: {e}")
    
#     try:
#         if 'first_name' not in mrz_data_dict:
#             # Fallback to capture first name in different structures
#             fallback_pattern_given_name = r'<([A-Z]+)<'
#             match_given_name = re.search(fallback_pattern_given_name, mrz_1)
#             if match_given_name:
#                 mrz_data_dict['first_name'] = match_given_name.group(1)
#     except Exception as e:
#         print(f"Error extracting first name for PSE: {e}")

#     return mrz_data_dict

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

# def extract_nationality(mrz_line):
#     match = re.match(r"^.{10}([A-Z]{3})", mrz_line)
#     if match:
#         return match.group(1)
#     else:
#         return None
    
# def palestine_passport_extraction(passport_text, api_key):
#     try:
#         logging.info(f"Starting Palestine Passport Extraction using api_key.{api_key[:4]}")
#         model = configure_genai(api_key)
#         jor_passport_result_ai = genai_vision_pse(passport_text, model)

#         logging.info(f"GenAI Raw Output: {jor_passport_result_ai}")
#         json_match = re.search(r'```(json|python|plaintext)?\s*(.*?)\s*```', jor_passport_result_ai, re.DOTALL)
#         if json_match:
#             json_str = json_match.group(2)
#             passport_final_result = json.loads(json_str)

#         else:
#             json_str = jor_passport_result_ai.replace('```json', '').replace('```', '').strip()
#             json_str = json_str.replace('null', 'None')
#             passport_final_result = eval(json_str)
        
#         try:
#             passport_final_result = mrz_add(passport_final_result)
#         except Exception as e:
#             print(f"Error adding MRZ data: {e}")

#         try:
#             passport_final_result = swap_dates_if_needed(passport_final_result)
#         except Exception as e:
#             print(f"Error swapping dates: {e}")

#         try:
#             passport_final_result = translate_arabic_words(passport_final_result)
#         except Exception as e:
#             print(f"Error translating: {e}")


#         if passport_final_result and not passport_final_result.get('passport_number', ''):
#             ## Passport Number Pattern
#             passport_number_pattern = r"(\d{8}|\d{7}|\d{6})"
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
            
#         ## Nationality Pattern
#         if 'nationality' not in passport_final_result:
#             try:
#                 nationality = extract_nationality(passport_final_result.get('mrz2', ''))
#                 passport_final_result['nationality'] = nationality
#             except:
#                 mrz2 = passport_final_result.get('mrz2', '')
#                 nationality_pattern = r'[A-Z]{3}'
#                 nationality_match = re.search(nationality_pattern, mrz2)
#                 if nationality_match:
#                     nationality = nationality_match.group(0)
#                     passport_final_result['nationality'] = nationality
#                 else:
#                     mrz2 = passport_final_result.get('mrz2', '')
#                     if mrz2:
#                         nationality = mrz2.split('<')[0][-3:]
#                         passport_final_result['nationality'] = nationality

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
#             passport_final_result['nationality'] = 'PSE'

#         if not passport_final_result.get('nationality', ''):
#             passport_final_result['nationality'] = 'PSE'

#         passport_final_result['issuing_country'] = 'PSE'

#         return passport_final_result

#     except Exception as e:
#         logging.error(f"Error occurred in GenAI: {e}")
#         print(f"Error occured in GenAI {e}")
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
    format='%(asctime)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    force=True
)

PROMPT_FRONT = """
Extract ALL fields from this Palestine Passport **front side** image with high accuracy.

Return a JSON object with the following fields (use the exact field names):

    - dob: Date of birth exactly as shown on the card (strictly preserve DD/MM/YYYY format)
    - expiry_date: Date of expiry exactly as shown on the card (strictly preserve DD/MM/YYYY format)
    - mrz1: First line of the MRZ, 
    - mrz2: Second line of the MRZ, 
    - full_name: Full name as printed on the card (extract exactly as written)
    - gender: Gender as either MALE or FEMALE (extract exactly as printed)
    - mother_name: Mother's Name (extract exactly as printed)
    - place_of_birth: Place of birth in English (extract exactly as printed)
    - issuing_date: Date of issue exactly as shown on the card (preserve original format)
    - place_of_issue: Place of issue as printed on the card
    - id_number: ID number as printed on the card (exactly 9 characters)
    - passport_number: Passport number as printed beside N° or No (exactly 7 characters)
    - header_verified: Return True if any of these texts are present in the image: P<PSE, PSE, PALESTINIAN AUTHORITY, or PALESTINE; otherwise False.
    - first_name: First name extracted from full_name (if full_name contains multiple words, use the first word)
    - last_name: Last name extracted from full_name (if full_name contains multiple words, use the last word)


Instructions:
    - Do NOT guess or hallucinate any values. If unclear, return empty string.
    - Only use information

"""
class PalestinePassportFront(BaseModel):
   

    dob: str = Field(...,
        description = "The date of birth exactly as shown on the card (strictly preserve DD/MM/YYYY format)",
    )
    expiry_date: str = Field(...,
        description = "The date of expiry exactly as shown on the card (strictly preserve DD/MM/YYYY format)",
    )

    mrz1: str = Field(..., 
        description="First line of the MRZ"
    )

    mrz2: str = Field(...,
        description="Second line of the MRZ"
    )

    full_name: str = Field(...,
                      description="Full name as printed on the card (extract exactly as written on the card)"
                      )

    gender: str = Field(...,
        description="Gender as either MALE or FEMALE , (printed as Sex, extract exactly as written on the card)"
    )

    mother_name: str = Field(
        ...,
        description="Mother's Name of the person (printed as Mother Name, extract exactly as written on the card)"
    )

    place_of_birth: str = Field(...,
        description = "The place of birth in english(printed as Birth Place, extract exactly as written on the card)",
    )

   
   
    issuing_date: str = Field(...,
        description = "The date of issue exactly as shown on the card (preserve DD/MM/YYYY format)",
    )

    place_of_issue: str = Field(...,
        description = "Place of issue as printed on the card.",
    )

    id_number: str = Field(..., min_length=9, max_length=9,
        description = "ID number as printed on the card, extract exactly as written on the card"
    )

    passport_number: str = Field(..., min_length=7, max_length=7,
        description = "Passport number as printed on the left side of passport beside i.e N° or No, extract exactly as written on the card"
    )

    header_verified: bool = Field(
        ...,
        description=" Return True if one of the texts present in the image P<PSE OR PSE OR PALESTINIAN AUTHORITY OR PALESTINE ",
    )

    first_name:  str = Field(
        ...,
        description="First name extracted from full_name",
    )
    last_name: str = Field(
        ...,
        description="Last name extracted from full_name",
    )
    
def process_image(side):

    if side == "first" or side=='page1':
        prompt = PROMPT_FRONT
        model = PalestinePassportFront

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


def get_response_from_openai_pse(image, side, country, openai_key):
    logging.info("Processing image for Palestinian passport extraction OPENAI......")
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
