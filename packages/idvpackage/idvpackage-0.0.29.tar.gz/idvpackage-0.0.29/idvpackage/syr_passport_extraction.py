# import google.generativeai as genai
# import base64
# import json
# import re
# import io
# from PIL import Image
# from datetime import datetime

# def configure_genai(api_key):
#     genai.configure(api_key=api_key)
#     model = genai.GenerativeModel(model_name="gemini-2.0-flash-lite")
#     return model

# def base64_to_image(base64_string):
#     image_data = base64.b64decode(base64_string)
#     image = Image.open(io.BytesIO(image_data))
#     return image

# def crop_image_in_half(image, offset=90):
#     width, height = image.size
#     split_line = (height // 2) - offset  # Make the first half smaller by 'offset' pixels
    
#     first_half = image.crop((0, 0, width, split_line))  
#     second_half = image.crop((0, split_line, width, height)) 

#     return first_half, second_half


# def is_valid_date(date_str):
#     date_pattern = re.compile(r'^(\d{2}/\d{2}/\d{4}|\d{4}/\d{2}/\d{2}|\d{4}-\d{2}-\d{2})$')
#     if date_str is None or date_pattern.match(date_str):
#         return True
#     else:
#         return False


# def genai_image_second_half(image, model):
#     result = model.generate_content(
#         [image, "\n\n", "give me issue_number, name, surname, father name, mother name, date_of_birth, place_of_birth, nationality, gender(M/F), and both lines of the MRZ from provided photo, please give me output as just dictionary - issue_number, full_name, first_name, last_name, father_name, mother_name, dob, place_of_birth, nationality,gender, mrz1, mrz2. Note that mrz1 is the line that starts with P"]
#     )
#     return  result.text


# def genai_vision_first_half(detected_text, model):
#     result = model.generate_content(
#         [detected_text,"\n\n", "Give me No from {detected_text}, output must be just dictionary - No"]
#     )#If the prompt includes the word "passport," it is flagged as harmful content.
#     return  result.text


# def genai_vision_second_half(detected_text, model):
#     result = model.generate_content(
#         [detected_text,"\n\n", "give me issue_number, passport_number, name, surname, father name, mother name, date_of_birth, place_of_birth, nationality, gender(M/F), and both lines of the MRZ from {detected_text}, please give me output as just dictionary - issue_number, passport_number, full_name, first_name, last_name, father_name, mother_name, dob, place_of_birth, nationality, gender, mrz1, mrz2. Note that mrz1 is the line that starts with P and contains name"]
#     )
#     return  result.text


# def genai_vision_mrz(detected_text, model):
#     result = model.generate_content(
#         [detected_text,"\n\n", "give me 'document_number', 'nationality', 'birth_date'(dd/mm/yyyy format), 'gender', 'expiration_date'(dd/mm/yyyy format) as dictionary from provided mrz. Dont write anything just return dictionary"]
#     )
#     return  result.text

# def fix_dob(passport_text):
#     dob = ''
#     expiry = ''
#     issue_date = ''
#     try:
#         matches = re.findall(r'\b\d{2}[\s/\-.]+\d{2}[\s/\-.]+\d{4}\b', passport_text, re.DOTALL)
#         date_objects = [datetime.strptime(re.sub(r'[\s/\-.]+', ' ', date).strip(), '%d %m %Y') for date in matches]
#         sorted_dates = sorted(date_objects)
#         sorted_date_strings = [date.strftime('%d %m %Y') for date in sorted_dates]

#         if len(sorted_date_strings) > 1:
#             dob = sorted_date_strings[0]
#             issue_date = sorted_date_strings[1]
#             expiry = sorted_date_strings[-1]
#     except:
#         matches = re.findall(r'\b\d{2}[./]\d{2}[./]\d{4}\b', passport_text)
#         date_objects = [datetime.strptime(date.replace('.', '/'), '%d/%m/%Y') for date in matches]
#         sorted_dates = sorted(date_objects)
#         sorted_date_strings = [date.strftime('%d/%m/%Y') for date in sorted_dates]

#         if len(sorted_date_strings)>1:
#             dob = sorted_date_strings[0]
#             issue_date = sorted_date_strings[1]
#             expiry = sorted_date_strings[-1]
#         else:
#             matches = re.findall(r'\d{4}-\d{2}-\d{2}', passport_text)
#             date_objects = [datetime.strptime(date, '%Y-%m-%d') for date in matches]
#             sorted_dates = sorted(date_objects)
#             sorted_date_strings = [date.strftime('%Y-%m-%d') for date in sorted_dates]

#             if len(sorted_date_strings)>1:
#                 dob = sorted_date_strings[0].replace('-', '/')
#                 issue_date = sorted_date_strings[1].replace('-', '/')
#                 expiry = sorted_date_strings[-1].replace('-', '/')
            
#             else:
#                 matches = re.findall(r'\d{2}-\d{2}-\d{4}', passport_text)
#                 date_objects = [datetime.strptime(date, '%d-%m-%Y') for date in matches]
#                 sorted_dates = sorted(date_objects)
#                 sorted_date_strings = [date.strftime('%d-%m-%Y') for date in sorted_dates]

#                 if sorted_date_strings:
#                     dob = sorted_date_strings[0].replace('-', '/')
#                     issue_date = sorted_date_strings[1].replace('-', '/')
#                     expiry = sorted_date_strings[-1].replace('-', '/')

#     print(f"\nDOB: {dob}, Issue Date: {issue_date}, Expiry: {expiry}\n")
#     return dob, issue_date, expiry

# def mrz_data(merged_dict, model):
#     # try:
#     input_mrz_2 = merged_dict['mrz2']
#     match = re.match(
#         r"(\d{10})([A-Z]{3})(\d{6})(\d)([MF])(\d{6})(\d)", 
#         input_mrz_2
#     )

#     if match:
#         birth_date_raw = match.group(3)
#         expiration_date_raw = match.group(6)

#         birth_year_prefix = '19' if int(birth_date_raw[:2]) > 23 else '20'
#         birth_date = f"{birth_date_raw[4:]}/{birth_date_raw[2:4]}/{birth_year_prefix}{birth_date_raw[:2]}"

#         exp_year_prefix = '19' if int(expiration_date_raw[:2]) > 50 else '20'
#         expiration_date = f"{expiration_date_raw[4:]}/{expiration_date_raw[2:4]}/{exp_year_prefix}{expiration_date_raw[:2]}"

#         result_dict = {
#             'passport_number': match.group(1),
#             'nationality': match.group(2),
#             'dob': birth_date, 
#             'gender': match.group(5),
#             'expiry_date': expiration_date
#         }
#         print(f"\nResult_dict from MRZ: {result_dict}\n")
#     else:
#         mrz_json = genai_vision_mrz(input_mrz_2, model)
#         json_str = mrz_json.replace('```json', '').replace('```', '').strip()
#         json_str = json_str.replace('null', 'None')
#         result_dict = eval(json_str)

#     result_dict_name = {}
#     input_mrz_1 = merged_dict['mrz1']
#     match = re.match(r"P[<N]SYR([A-Z<]+)<<*([A-Z]+)<<*", input_mrz_1)
#     if match:
#         result_dict_name = {
#             'last_name': match.group(1),
#             'first_name': match.group(2)
#         }
#         result_dict_name['last_name'] = result_dict_name['last_name'].replace('<', ' ').strip()
#         result_dict_name['first_name'] = result_dict_name['first_name'].replace('<', ' ').strip()
        
#     else:
#         match = re.match(r"PNSYR\s*([A-Za-z]+)(?:<+([A-Za-z]+))?<<*", input_mrz_1)
#         if match:
#             try:
#                 result_dict_name = {
#                     'last_name': match.group(1),
#                     'first_name': match.group(2)
#                 }
#                 result_dict_name['last_name'] = result_dict_name['last_name'].replace('<', ' ').strip()
#                 result_dict_name['first_name'] = result_dict_name['first_name'].replace('<', ' ').strip()
#             except Exception as e:
#                 result_dict_name = {}
#                 print(f"Error: {e}")

#     # Merge the name data and other MRZ data into dict_gemini
#     merged_dict_mrz = {**merged_dict, **result_dict_name, **result_dict}

#     # except Exception as e:
#     #     print(f"Error: {e}")

#     return merged_dict_mrz


# def fill_with_mrz(dict_gemini, mrz_dict_final):
#     fields_to_fill = ['last_name', 'first_name', 'nationality', 'dob', 'gender']
#     for field in fields_to_fill:
#         if not dict_gemini.get(field, ''):
#             dict_gemini[field] = mrz_dict_final.get(field, '')
#     return dict_gemini


# def extract_passport_number(input_string):
#     pattern = r'^(\d+)(?=[A-Z]{3})'
    
#     match = re.search(pattern, input_string)
    
#     if match:
#         return match.group(1)
#     else:
#         return None
    
# def syr_passport_extraction_front(passport_text_first, api_key):
#     model = configure_genai(api_key)
#     try:
#         ## Process first half of the image
#         passport_first_ai_result = genai_vision_second_half(passport_text_first, model)
#         json_match = re.search(r'```(json|python|plaintext)?\s*(.*?)\s*```', passport_first_ai_result, re.DOTALL)
#         if json_match:
#             json_str = json_match.group(2)
#             dictionary_first_half = json.loads(json_str)

#         else:
#             json_str = passport_first_ai_result.replace('```json', '').replace('```', '').strip()
#             json_str = json_str.replace('null', 'None')
#             dictionary_first_half= eval(json_str)
        
#         if dictionary_first_half.get('nationality', ''):
#             if dictionary_first_half['nationality'].lower().startswith('syria'):
#                 dictionary_first_half['nationality'] = 'SYR'

#     except Exception as e:
#         print(f"Error occured in GenAI first half {e}")

#     if dictionary_first_half and dictionary_first_half.get('passport_number', ''):
#         passport_number = dictionary_first_half.pop('passport_number')
#         passport_number = re.sub(r'\D', '', passport_number)

#         dictionary_first_half['passport_number'] = passport_number

#     merged_dict = {**dictionary_first_half}

#     if merged_dict and merged_dict.get('birth_date', ''):
#         merged_dict['dob'] = merged_dict.pop('birth_date')
    
#     if merged_dict and merged_dict.get('birth_place', ''):
#         merged_dict['place_of_birth'] = merged_dict.pop('birth_place')
    
#     if merged_dict and (
#         not merged_dict.get('dob') or
#         not merged_dict.get('full_name') or
#         not merged_dict.get('nationality') or
#         not merged_dict.get('first_name') or
#         not merged_dict.get('last_name')
#     ):
#         mrz_dict_final = mrz_data(merged_dict, model)
#         merged_dict = fill_with_mrz(merged_dict, mrz_dict_final)
    
#     passport_text = passport_text_first
#     if merged_dict and not merged_dict.get('dob', ''):
#         dob, issue_date, expiry = fix_dob(passport_text)
#         merged_dict['dob'] = dob

#     if not merged_dict.get('full_name', ''):
#         merged_dict['full_name'] = f"{merged_dict.get('first_name', '')} {merged_dict.get('last_name', '')}"

#     if not merged_dict.get('passport_number', ''):
#         passport_number = extract_passport_number(merged_dict.get('mrz2', ''))
#         merged_dict['passport_number'] = passport_number

#     if merged_dict.get('passport_number', ''):
#         passport_number = merged_dict['passport_number']
#         if len(passport_number) < 9:
#             passport_number = f"0{passport_number}"
#         merged_dict['passport_number'] = passport_number
    
#     if merged_dict.get('passport_number', ''):
#         merged_dict['id_number'] = merged_dict['passport_number']

#     if not merged_dict.get('mrz', ''):
#         mrz1 = merged_dict.get('mrz1', '')
#         mrz2 = merged_dict.get('mrz2', '')
#         if mrz1 and mrz2:
#             merged_dict['mrz'] = f"{mrz1} {mrz2}"

#     if "gender" in merged_dict:
#         gender = merged_dict["gender"].strip().upper()
#         if gender == "F":
#             merged_dict["gender"] = "FEMALE"
#         elif gender == "M":
#             merged_dict["gender"] = "MALE"

#     if 'gender' in merged_dict:
#         merged_dict["gender"] = merged_dict["gender"].strip().upper()

#     if merged_dict.get('nationality', ''):
#         nationality = merged_dict.get('nationality', '')
#         if nationality and len(nationality.split(' ')) > 1:
#             merged_dict['nationality'] = 'SYR'

#     if not merged_dict.get('nationality', ''):
#         merged_dict['nationality'] = 'SYR'
    
#     merged_dict['issuing_country'] = 'SYR'

#     return merged_dict

# def genai_vision_back(detected_text, model):
#     result = model.generate_content(
#         [detected_text,"\n\n", "give me date of issue(in dd/mm/yy format), expiry date (in dd/mm/yy format), place of issue, and national number from {detected_text}, please give me output as just dictionary - issuing_date, expiry_date, place_of_issue, national_number"]
#     )
#     return  result.text

# def find_issue_date_and_expiry(passport_text_back):
#     date_pattern = re.compile(r'\b\d{2}/\d{2}/\d{4}\b')
#     matches = date_pattern.findall(passport_text_back)
    
#     if not matches:
#         return None, None
    
#     date_objects = [datetime.strptime(date, '%d/%m/%Y') for date in matches]
#     sorted_dates = sorted(date_objects)
    
#     issuing_date = sorted_dates[0].strftime('%d/%m/%Y')
#     expiry_date = sorted_dates[-1].strftime('%d/%m/%Y')
    
#     return issuing_date, expiry_date

# def extract_national_number(passport_text_back):
#     national_number_pattern = re.compile(r'\b\d{3}-\d{8}\b')
#     match = national_number_pattern.search(passport_text_back)
    
#     if match:
#         return match.group(0)
#     else:
#         return None
    

# def syr_passport_extraction_back(passport_text_back, api_key):
#     model = configure_genai(api_key)
#     place_of_issue = ''
#     result_ai = genai_vision_back(passport_text_back, model)
#     try:
#         json_str = result_ai.replace('```json', '').replace('```', '').strip()
#         json_str = json_str.replace('null', 'None')
#         try:
#             passport_back_data = eval(json_str)
#             issue_date = passport_back_data.get('issuing_date', '')
#             expiry_date = passport_back_data.get('expiry_date', '')
#             # Validate date format
#             if not is_valid_date(issue_date) or not is_valid_date(expiry_date):
#                 raise ValueError("Invalid date format")

#         except Exception as e:
#             print(f"Error in parsing or validating dates: {e}")
#             passport_back_data = {'issuing_date': '', 'expiry_date': '', 'national_number': '', 'place_of_issue': ''}
#             try:
#                 issue_date, expiry = find_issue_date_and_expiry(passport_text_back)
#                 if issue_date and expiry:
#                     passport_back_data = {
#                     'issuing_date': issue_date,
#                     'expiry_date': expiry
#                     }
                
#                 national_number = extract_national_number(passport_text_back)
#                 if national_number:
#                     passport_back_data['national_number'] = national_number

#             except Exception as e:
#                 print(f"Error occurred in finding dates: {e}")
#                 passport_back_data = {}
    
#     except Exception as e:
#         print(f"Error occured in GenAI back {e}")
#         passport_back_data = {}
#         try:
#             issue_date, expiry = find_issue_date_and_expiry(passport_text_back)
#             if issue_date and expiry:
#                 passport_back_data = {
#                     'issuing_date': issue_date,
#                     'expiry_date': expiry
#                 }

#             national_number = extract_national_number(passport_text_back)
#             if national_number:
#                 passport_back_data['national_number'] = national_number

#         except Exception as e:
#             print(f"Error occured in finding dates {e}")
#             passport_back_data = {}

#     if not passport_back_data.get('place_of_issue', ''):
#         json_match = re.search(r'```(json|python|plaintext)?\s*(.*?)\s*```', result_ai, re.DOTALL)
#         if json_match:
#             json_str = json_match.group(2)
#             dictionary_second_half = json.loads(json_str)
#             place_of_issue = dictionary_second_half.get('place_of_issue', '')
#             passport_back_data['place_of_issue'] = place_of_issue

#         else:
#             json_str = result_ai.replace('```json', '').replace('```', '').strip()
#             json_str = json_str.replace('null', 'None')
#             dictionary_second_half= eval(json_str)

#             place_of_issue = dictionary_second_half.get('place_of_issue', '')
#             passport_back_data['place_of_issue'] = place_of_issue
#     else:
#         passport_back_data['place_of_issue'] = ''
        
#     return passport_back_data 


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
Extract ALL fields from this Syrian Passport front side image with high accuracy.

Return a JSON object with the following fields (use the exact field names):

- first_name: Given Name (extract exactly as written on the card)
- last_name: Surname (extract exactly as written on the card)
- father_name: Father's Name (extract exactly as written on the card)
- mother_name: Mother's Name (extract exactly as written on the card)
- dob: Date of birth exactly as shown on the card (preserve original format)
- place_of_birth: Place of birth in English (extract exactly as written on the card)
- mrz1: First line of the MRZ, exactly 44 characters, pad with '<' at the end if shorter
- mrz2: Second line of the MRZ, exactly 44 characters
- gender: Gender as either MALE or FEMALE (extract exactly as printed)
- header_verified: True if both 'SYRIAN ARAB REPUBLIC' and 'PASSPORT' are clearly visible, else False
- country_code: Country code as printed below the text 'country code' (extract exactly as written)
- issue_number: Issue number as printed on the card as 'Issue no' (extract exactly as written)

Instructions:
- Do NOT guess or hallucinate any values. If unclear, return null.
- Only use information visible on the card.
- Return the result as a single JSON object matching the schema above.
"""

PROMPT_BACK = """
Extract ALL fields from this Syrian Passport back side image with high accuracy.

Return a JSON object with the following fields (use the exact field names):

- issue_date: Issue date in DD/MM/YYYY format (extract exactly as printed)
- place_of_issue: Place of issue as printed on the card
- expiry_date: Expiry date in DD/MM/YYYY format (extract exactly as printed)
- national_number: National number as printed on the card (example: 123-12345678)

Instructions:
- Do NOT guess or hallucinate any values. If a field is faint, blurry, or unclear, return null.
- Only use information visible on the card.
- Return the result as a single JSON object matching the schema above.
"""


class SyriaPassportFront(BaseModel):
   

    first_name: str = Field(...,
                             description = "Name of the person ( printed as Given Name, extract exactly as written on the card)")
    
    last_name: str = Field(...,
                            description = "Surname of the person ( printed as Surname. extract exactly as written on the card)")
    
    father_name: str = Field(
        ...,
        description="Father's Name of the person (printed as Father Name, extract exactly as written on the card)",
    )

    mother_name: str = Field(
        ...,
        description="Mother's Name of the person (printed as Mother Name, extract exactly as written on the card)",
    )
    
    dob: str = Field(
        ...,
        description="The date of birth exactly as shown on the card (preserve original format)",
    )

    place_of_birth: str = Field(
        ...,
        description = "The place of birth in english(printed as Birth Place, extract exactly as written on the card)",
    )


    mrz1: str = Field(..., min_length=44, max_length=44,
        description="First line of the MRZ, exactly 44 characters, padded with '<' at the end if shorter"
    )

    mrz2: str = Field(..., min_length=44, max_length=44,
        description="Second line of the MRZ, exactly 44 characters"
    )

    gender: str = Field(..., description="Gender as either MALE or FEMALE (printed as Sex on the card)")


    header_verified: bool = Field(
        ...,
        description="Whether the standard header text (SYRIAN ARAB REPUBLIC) is present in the image.",
    )

    country_code: str = Field(
        ...,
        description="The country code,(value is printed below the text country code, extract exactly as written on the card)",
    )

    issue_number: str = Field(  
        ...,
        description="Issue number as printed on the card as 'Issue no' (extract exactly as written)",
    )

class SyriaPassportBack(BaseModel):

    
    issue_date: str = Field(..., description="Issue date in DD/MM/YYYY format")
    place_of_issue: str = Field(..., description="Place of issue as printed on the card")
    expiry_date: str = Field(..., description="Expiry date in DD/MM/YYYY format")

    national_number: str = Field(..., description="national number as printed on the card example: 123-12345678")

    
 
def process_image(side):

    if side == "first" or side == "page1":
        prompt = PROMPT_FRONT
        model = SyriaPassportFront

    elif side == "back" or side == "page2":
        prompt = PROMPT_BACK
        model = SyriaPassportBack

    
    else:
        raise ValueError("Invalid document side specified. Use 'front', 'back', or 'passport'.")

    return model, prompt

def get_openai_response(prompt: str, model_type, image: BytesIO, openai_key):
    b64_image = base64.b64encode(image.getvalue()).decode("utf-8")
    for attempt in range(3):
        try:
            client = OpenAI(api_key=openai_key)
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

def get_response_from_openai_syr(image, side, country, openai_key):

    logging.info("Processing image for Syria passport extraction OPENAI......")
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