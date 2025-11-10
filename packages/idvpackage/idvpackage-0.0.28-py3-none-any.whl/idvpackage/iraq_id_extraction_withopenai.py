# import json
# import time
# import datetime
# import openai
# from langchain.tools import tool
# from langchain.tools.render import format_tool_to_openai_function
# from langchain.prompts import ChatPromptTemplate
# from langchain.chat_models import ChatOpenAI
# from pydantic import BaseModel, Field, validator
# from langchain.utils.openai_functions import convert_pydantic_to_openai_function
# from typing import Optional, Literal
# from langchain.output_parsers.openai_functions import JsonOutputFunctionsParser
# from langchain.agents.output_parsers import OpenAIFunctionsAgentOutputParser
# import idvpackage.genai_utils as genai_utils
# import idvpackage.genai_utils as sanity_utils
# from datetime import datetime, timedelta
# from dateutil.relativedelta import relativedelta
# from pydantic import ValidationError
# import logging
# from langchain.schema.agent import AgentFinish
import base64
import time
from io import BytesIO
from typing import Set, List, Optional
import json
import cv2
import torch
from PIL import Image
from openai import OpenAI
from pydantic import BaseModel, Field, validator
import logging



logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    force=True
)

# class Verify_IRQ_Passport(BaseModel):
#     """Validates whether a given OCR text represents a valid Iraqi Passport"""
#     is_valid_id: Literal["True", "False"] = Field(..., description="Return True if document is a valid Iraqi Passport" 
#             "It should contain Arabic/Kurdish text like: جمهورية العراق, کۆماری عێراق and English Text: Republic of Iraq"
#             "Return False otherwise.")
#     side: Literal["passport", ""] = Field(..., description="Return passport if the document is a valid Iraqi Passport")

# class Iraq_Passport(BaseModel):
#     """Extract the fields from the OCR extracted text of an Iraqi Passport"""
#     full_name: str = Field(..., description="Full name of the person on the passport")
#     last_name: str = Field(..., description="Surname of the person on the passport")
#     dob: str = Field(..., description="Date of Birth")
#     place_of_birth: str = Field(...,
#         description=(
#             "Place of Birth of the person on the passport"
#             "DO NOT mix it up with Issuing Authority"
#             "Translate to English"
#         )
#     )
#     mother_name: str = Field(..., description="Mother's full name")
#     gender_letter: str = Field(..., description="Gender/Sex of the person on the passport. It is either M or F.")
#     issuing_authority: str = Field(...,
#         description=(
#             "Issuing Authority"
#             "Translate to English"
#         )
#     )
#     nationality: str = Field(..., description="Nationality in ISO 3166-1 alpha-3 format (e.g., 'IRQ' for Iraqi, 'JOR' for Jordanian)", example="IRQ")
#     issuing_country: str = Field(..., description="Issuing Country/Country Code (e.g. 'IRQ', 'JOR')", example='IRQ')
#     id_number: str = Field(..., description="9-character alphanumeric passport number.")
#     mrz1: str = Field(...,
#                       description=(
#                           "MRZ Line 1."
#                           "Should be exactly 44 characters long."
#                           "If OCR splits it across lines, join them into one."
#                           "Do not confuse with MRZ Line 2 — Line 1 typically starts with 'P<' and contains names."
#                       )
#                       )

#     mrz2: str = Field(...,
#                       description=(
#                           "MRZ Line 2."
#                           "Should be exactly 44 characters long."
#                           "If OCR splits it across lines, join them into one string."
#                           "Do not confuse with MRZ Line 1 — Line 2 contains passport number, nationality, DOB, expiry, etc."
#                       )
#                       )

#     @validator("mrz2")
#     def validate_mrz2_content_length(cls, v):
#         if len(v.replace('<', '')) < 28:
#             raise ValueError("cropped_mrz")
#         return v


# @tool(args_schema=Iraq_Passport)
# def sanity_check_irq_passport(full_name='',
#                               last_name='',
#                               dob='',
#                               place_of_birth='',
#                               mother_name='',
#                               gender_letter='',
#                               issuing_authority='',
#                               nationality='',
#                               issuing_country='',
#                               id_number='',
#                               mrz='',
#                               mrz1='',
#                               mrz2=''):
#     try:

#         # if len(mrz1)<44:
#         #     return {'error':'covered_photo','error_details':'cropped mrz'}
#         #
#         # if len(mrz2)<44:
#         #     return {'error': 'covered_photo', 'error_details': 'cropped mrz'}

#         # if len(mrz2.replace('<',''))<30:
#         #     return {'error': 'covered_photo', 'error_details': 'cropped mrz'}


#         mrz = mrz1 + mrz2



#         id_number = mrz2[0:9]

#         if id_number[0] == '8':
#             id_number = 'B' + id_number[1:]

#         expiry_date = mrz2.replace(" ", "")[21:27]
#         expiry_date = sanity_utils.parse_yymmdd(expiry_date)  # string 'YYYY-MM-DD'
#         is_doc_expired = sanity_utils.is_expired_id(expiry_date)

#         if is_doc_expired:
#             return {"error": "expired_id", "error_details": "expired ID"}

#         # Reuse expiry_date for datetime object temporarily for calculations
#         expiry_date_obj = datetime.strptime(expiry_date, "%Y-%m-%d")
#         issue_date = (expiry_date_obj - relativedelta(years=8) + timedelta(days=1)).strftime("%Y-%m-%d")
#         try:
#             dob = sanity_utils.convert_dob_to_standard(dob)
#             expiry_date = sanity_utils.convert_dob_to_standard(expiry_date)
#         except Exception as e:
#             return {"error": "covered_photo", "error_details": "Exception Thrown while parsing dates: {e}"}



#         if gender_letter.lower() not in ['m','f','male','female']:
#             gender_letter = mrz2[20]

#         if gender_letter.lower()=='m':
#             gender = 'Male'
#         elif gender_letter.lower()=='f':
#             gender = 'Female'


#         optional_fields = [gender_letter]
#         required_fields = {k: v for k, v in locals().items() if k not in optional_fields}

#         missing = [key for key, value in required_fields.items() if not str(value).strip()]
#         if missing:
#             return {
#                 'error': 'covered_photo',
#                 'error_details': f'Missing or empty fields: {", ".join(missing)}'
#             }
#         result =  {
#             "error": "",
#             "error_details": "",
#             "doc_type":"passport",
#             **locals()
#         }

#         if 'expiry_date_obj' in result.keys():
#             del result['expiry_date_obj']
#         if 'optional_fields' in result.keys():
#             del result['optional_fields']
#         if 'required_fields' in result.keys():
#             del result['required_fields']
#         if 'missing' in result.keys():
#             del result['missing']
#         return result
#     except Exception as e:
#         return {'error':'covered_photo','error_details':e}


# class Verify_IRQ_ID(BaseModel):
#     """Validates whether a given OCR text represents a valid Iraqi National ID (either front or back side)."""
#     is_valid_id: Literal["True", ""] = Field(..., description="Return True if document is either a valid Iraqi National ID's front side or back side." 
#             "It should contain Arabic/Kurdish text like: جمهورية العراق / وزارة الداخلية"
#             "مديرية الأحوال المدنية والجوازات والاقامة"
#             "کوماری عیراق / وه زاره تی ناوخو"
#             "پریود به را بائی باری شارستانی و پاسپورت و نیشنگه"
#             "جمهورية العراق / وزارة الداخلية"
#             "کوماری عیراق / وه زاره تی ناوخو"
#             "Return empty string '' otherwise.")
#     side: Literal["front","back",""] = Field(..., description="Determine from the given ocr text, if this is a front side or back side of an Iraqi National ID. Return empty string if its neither."
#                                              "A back side has three lines of MRZ, has dates of birth, issue and expiry"
#                                              "A front side has names, and id number. No dates.")

# class Iraq_National_ID_front(BaseModel):
#     """Extract the fields from the OCR extracted text of an Iraqi National ID's front side. Front Side has names, (like father name, mother name etc.), national id numbers but has no dates. Translate wherever required."""
#     first_name: str = Field(..., description="First name (الاسم / ناو) in Arabic.")
#     first_name_en: str = Field(..., description="First name (الاسم / ناو), translated to English.")
#     father_name: str = Field(..., description="Father's name (الأب / باوك) in Arabic.")
#     father_name_en: str = Field(..., description="Father's name (الأب / باوك), translated to English.")
#     third_name: str = Field(..., description="Paternal grandfather's name (الجد / بابير) in Arabic.")
#     third_name_en: str = Field(..., description="Paternal grandfather's name (الجد / بابير), translated to English.")
#     last_name: Optional[str] = Field(
#         "",
#         description=(
#             "Family/tribal name (اللقب / نازناو) in Arabic. "
#             "OCR extracts various versions of 'نازناو' like الزناو, الزنار; do not interpret them as the family name."
#         )
#     )
#     last_name_en: Optional[str] = Field(
#         "",
#         description=(
#             "Family/tribal name (اللقب / نازناو), translated to English. "
#             "OCR extracts various versions of 'نازناو' like الزناو, الزنار; do not interpret them as the family name."
#         )
#     )
#     mother_first_name: str = Field(..., description="Mother's name (الام/ دابك) in Arabic.")
#     mother_first_name_en: str = Field(..., description="Mother's name (الام/ دابك), translated to English.")
#     mother_last_name: str = Field(..., description="Maternal grandfather's name (الجد / بابير) in Arabic.")
#     mother_last_name_en: str = Field(..., description="Maternal grandfather's name (الجد / بابير), translated to English.")
#     gender_ar: str = Field(..., description="Gender (الجنس / ردگار): ذكر (male) or أنثى (female).")
#     gender: str = Field(..., description="Gender (الجنس / ردگار), translated to English")
#     id_number_front: str = Field(..., description="12-digit national ID number.")
#     card_number_front: str = Field(..., description="9-character alphanumeric document number.")
#     serial_number: Optional[str] = Field("", description="6-digit card serial number.")
#     blood_type: Optional[str] = Field(None, description="Blood type (e.g., O+, A-).")

# @tool(args_schema=Iraq_National_ID_front)
# def sanity_check_irq_front(
#     id_number_front='',
#     card_number_front='',
#     first_name='',
#     first_name_en='',
#     father_name='',
#     father_name_en='',
#     third_name='',
#     third_name_en='',
#     last_name='',
#     last_name_en='',
#     mother_first_name='',
#     mother_first_name_en='',
#     mother_last_name='',
#     mother_last_name_en='',
#     gender_ar='',
#     gender='',
#     blood_type='',
#     serial_number=''

# ) -> dict:
#     print("SANITY CHECK IRQ FRONT WAS CALLED")
#     """Run sanity checks on the data extracted from Iraq national ID's front side."""
#     #Post-Processing steps
#     try:
#         if not id_number_front.isdigit() or len(id_number_front) != 12:
#             return {'error': 'invalid_national_number', 'error_details': 'invalid national number, please take a clearer picture of your image. Note: We do not accept Civil Status IDs.'}

#         if len(card_number_front) != 9:
#             return {'error': 'invalid_document_number', 'error_details': 'invalid document number, please take a clearer picture of your image. Note: We do not accept Civil Status IDs.'}

#         doc_type = 'national_identity_card'
#         #at this point, verify_irq_id has run, so we can safely assume the nationality here is IRQ
#         nationality='IRQ'
#         nationality_en = 'IRQ'

#         optional_fields = ('last_name', 'last_name_en','serial_number','blood_type')
#         required_fields = {k: v for k, v in locals().items() if k not in optional_fields}

#         result_dict = {**locals()}






#         if not last_name or not last_name_en:
#             name = result_dict.get('first_name', '') + " " + result_dict.get('father_name', '')
#             name_en = result_dict.get('first_name_en', '') + " " + result_dict.get('father_name_en', '')
#         else:
#             name = result_dict.get('first_name', '') + " " + result_dict.get('father_name', '') + " " + result_dict.get('last_name','')
#             name_en = result_dict.get('first_name_en', '') + " " + result_dict.get('father_name_en', '')+ " " + result_dict.get("last_name_en",'')

#         missing = [key for key, value in required_fields.items() if not str(value).strip()]
#         if missing:
#             return {'error': 'covered_photo', 'error_details': f'Missing or empty fields: {", ".join(missing)}'}

#         result =  {
#             "error": "",
#             "error_details": "",
#             **locals()
#         }

#         if 'required_fields' in result.keys():
#             del result['required_fields']
#         if 'missing' in result.keys():
#             del result['missing']
#         if 'optional_fields' in result.keys():
#             del result['optional_fields']
#         if 'result_dict' in result.keys():
#             del result['result_dict']
#         return result

#     except Exception as e:
#         return {'error':'covered_photo','error_details':e}



# class Iraq_National_ID_back(BaseModel):
#     """Extract only the Arabic fields from the OCR text of an Iraqi National ID's back side. A back side has fields like dates: issue, expiry, birth. Translate where required."""
#     issuing_authority: str = Field(..., description="Issuing authority (جهة الاصدار / لايانى ددرجوون) in Arabic")
#     issuing_authority_en: str = Field(..., description="Issuing authority (جهة الاصدار / لايانى ددرجوون), translated to English")
#     issue_date: str = Field(..., description="Date of issue")
#     expiry_date: str = Field(..., description="Date of expiry")
#     place_of_birth: str = Field(..., description="Place of birth in Arabic.")
#     place_of_birth_en: str = Field(..., description="Place of birth, translated to English.")
#     dob: str = Field(..., description="Date of birth")
#     family_number: str = Field(..., description='18-character alphanumeric Family number (الرقم العائلي / ژمارەى خێزانی)')
#     mrz1: str = Field(...,description="MRZ Line 1: Includes document type (ID), issuing country code (IRQ), document number, and check digits. Example: 'IDIRQAL36266736200026108063<<<'")
#     mrz2: str = Field(...,description="MRZ Line 2: Encodes date of birth (YYMMDD), gender (M/F), expiry date (YYMMDD), and nationality code (IRQ) and check digit at the end of '<<<<<<'. Example: '0007191M2811280IRQ<<<<<<<<<<<7'")
#     mrz3: str = Field(...,description="MRZ Line 3: Contains surname and given name(s), separated by '<<'. Given names may include multiple parts separated by '<'. If no surname is present, it starts with '<<'. Example: 'AHMED<<ALI<HASSAN' or '<<ALI'")
#     last_name_back: str = Field(...,description="Surname extracted from MRZ line 3, before the '<<' separator.")
#     first_name_back: str = Field(...,description="Given name extracted from MRZ line 3, after the '<<' seperator.")


# @tool(args_schema=Iraq_National_ID_back)
# def sanity_check_irq_back(
#     issuing_authority='',
#     issuing_authority_en='',
#     issue_date='',
#     expiry_date='',
#     place_of_birth='',
#     place_of_birth_en='',
#     dob='', mrz1='', mrz2='', mrz3='',
#     last_name_back='',
#     first_name_back='',
#     family_number=''
# ):
#     try:
#         #===========Post-Processing==============
#         print("SANITY CHECK IRQ BACK WAS CALLED")
#         """Run sanity checks on the data extracted from Iraq national ID's back side."""
#         doc_type = 'national_identity_card'

#         family_number = sanity_utils.fix_family_number(family_number)

#         family_number_en = family_number

#         #At this point, verify_irq_id has been run, so we can safely say its an Iraqi ID.
#         nationality='IRQ'
#         issuing_country='IRQ'

#         if mrz1:
#             card_number = mrz1.strip()[5:14]
#             card_number_back = mrz1.strip()[5:15]
#             id_number = mrz1.strip()[15:27]
#             mrz = [mrz1 + mrz2 + mrz3]

#         else:
#             return {'error':'covered_photo', 'error_details':'cropped_mrz'}



#         #==============Sanity checks for blur detection and/or cropped image
#         valid_expiry_issue = sanity_utils.is_expiry_issue_diff_valid(issue_date,expiry_date, 10)
#         age_check = sanity_utils.is_age_18_above(dob)
#         dob_match_mrz_dob = sanity_utils.is_mrz_dob_mrz_field_match(dob, mrz2)

#         is_doc_expired = sanity_utils.is_expired_id(expiry_date)

#         if is_doc_expired:
#             return {"error":"expired_id", 'error_details':'expired ID'}

#         if mrz2:
#             gender_back = sanity_utils.find_gender_from_back(mrz2.strip())
#         else:
#             gender_back=''



#         if not (all([valid_expiry_issue, age_check, dob_match_mrz_dob])):
#             return {'error':'covered_photo', 'error_details':'blur or cropped or low-quality image'}


#         #Check required fields
#         optional_fields = ('last_name_back','first_name_back')
#         required_fields = {k: v for k, v in locals().items() if k not in optional_fields}

#         missing = [key for key, value in required_fields.items() if not str(value).strip()]
#         if missing:
#             return {
#                 'error': 'covered_photo',
#                 'error_details': f'Missing or empty fields: {", ".join(missing)}'
#             }
#         try:
#             dob = sanity_utils.convert_dob_to_standard(dob)
#             expiry_date = sanity_utils.convert_dob_to_standard(expiry_date)
#         except Exception as e:
#             return {
#                 'error': 'covered_photo',
#                 'error_details': f'Exception Thrown while parsing dates: {e}'
#             }


#         result =  {
#             "error": "",
#             "error_details": "",
#             **locals()
#         }

#         if 'required_fields' in result.keys():
#             del result['required_fields']
#         if 'missing' in result.keys():
#             del result['missing']
#         if 'optional_fields' in result.keys():
#             del result['optional_fields']
#         return result
#     except Exception as e:
#         return {'error':'covered_photo','error_details':e}



# def route(result):
#     if isinstance(result, AgentFinish):
#         return {'error': 'covered_photo', 'error_details': result.return_values['output']}
#     else:
#         tools = {
#             "sanity_check_irq_back": sanity_check_irq_back,
#             "sanity_check_irq_front": sanity_check_irq_front,
#             "sanity_check_irq_passport": sanity_check_irq_passport
#         }
#         return tools[result.tool].run(result.tool_input)

# def route_verification(result):
#     if isinstance(result,AgentFinish):
#         return ''
#     else:
#         return result.tool_input

# def extraction_chain(ocr_text, openai_key, side = ''):
#     try:
#         gpt_model = 'gpt-4o'
#         print("WE ARE IN EXTRACTION CHAIN")
#         tools_func = [sanity_check_irq_back, sanity_check_irq_front, sanity_check_irq_passport]

#         model = ChatOpenAI(model=gpt_model, temperature=0,
#                            openai_api_key=openai_key)
#         extraction_functions = [format_tool_to_openai_function(f) for f in tools_func]
#         extraction_model = model.bind(functions=extraction_functions)

#         prompt = ChatPromptTemplate.from_messages([
#             ("system",
#              "Extract the relevant information, if not explicitly provided do not guess, leave empty string. Extract partial info. Translate values wherever it is required."
#              ),
#             ("user", "{ocr_text}")
#         ])

#         prompt_verify_doc = ChatPromptTemplate.from_messages([
#             ("system", "Verify the relevant document."
#              ),
#             ("user", "{ocr_text}")
#         ])

#         model_verification = ChatOpenAI(model=gpt_model, temperature=0,
#                            openai_api_key=openai_key)
#         verification_function = [convert_pydantic_to_openai_function(Verify_IRQ_ID), convert_pydantic_to_openai_function(Verify_IRQ_Passport)]
#         verification_model = model_verification.bind(functions=verification_function)
#         verification_chain = prompt_verify_doc | verification_model | OpenAIFunctionsAgentOutputParser() | route_verification
#         st = time.time()
#         verification_model_result = verification_chain.invoke({"ocr_text":ocr_text})
#         logging.info(f'----------------Time taken for Verification Chain: {time.time() - st} seconds\n')
#         if verification_model_result == '':
#             if side=='front':
#                 return {'error':f'not_front_id'}, ''
#             if side=='back':
#                 return {'error':f'not_back_id'}, ''
#             if side=='page1':
#                 return {'error': f'not_passport'}, ''
#             else:
#                 return {'error':'covered_photo'}
#         else:
#             is_valid_id = verification_model_result.get("is_valid_id","")


#             if verification_model_result.get("side","")=='passport':
#                 side_predicted='page1'

#             else:
#                 side_predicted = verification_model_result.get("side","")
#             print("Side Predicted:", side_predicted)



#         if is_valid_id=="True" and side==side_predicted:
#             max_retries = 2
#             st = time.time()
#             for attempt in range(max_retries+1):
#                 extraction_chain = prompt | extraction_model | OpenAIFunctionsAgentOutputParser() | route
#                 data = extraction_chain.invoke({"ocr_text": ocr_text})

#                 if data.get('error')=='':
#                     return data, side_predicted
#                 if data.get('error')!='' and attempt>=max_retries:
#                     return data, side_predicted
#                 elif data.get('error')!='' and attempt<max_retries:
#                     print("RETRYING")
#                     time.sleep(2)
#                     continue
#         #Only for testing purpose, comment out when pushing to production.
#         # if is_valid_id=="True" and side=='auto':
#         #     max_retries = 2
#         #     for attempt in range(max_retries+1):
#         #         extraction_chain = prompt | extraction_model | OpenAIFunctionsAgentOutputParser() | route
#         #         data = extraction_chain.invoke({"ocr_text": ocr_text})

#                 if data.get('error')=='':
#                     return data, side_predicted
#                 if data.get('error')!='' and attempt>=max_retries:
#                     return data, side_predicted
#                 elif data.get('error')!='' and attempt<max_retries:
#                     print("RETRYING")
#                     time.sleep(2)
#                     continue
#             logging.info(f'----------------Time taken for Extraction Chain: {time.time() - st} seconds\n')

#         else:
#             if side=='' or side=='auto':
#                 side = side_predicted
#                 error = f"not_{side}_id"
#                 return {'error':error}, side
#             if side=='front' or side=='back':
#                 return {'error':f'not_{side}_id'}, side
#             elif side=='page1':
#                 return {'error':'not_passport'}, side

#     except ValidationError as e:
#         errors = e.errors()  # list of error dicts
#         # Extract all messages
#         error = [error['msg'] for error in errors]
#         return {'error':error[0], 'error_details': 'cropped mrz'},''
#     except Exception as e:
#         return {'error':'bad_image', 'error_details':e}, ''

# from idvpackage.llm_ocr import llm_ocr_extraction
#
# def ocr_and_extraction(base_64_image, openai_key, side):
#     openai.api_key = openai_key
#     ocr_text = llm_ocr_extraction(base_64_image)
#     result,side =  extraction_chain(ocr_text, openai_key,side)
#     return ocr_text,result,side


# use response.pareser method to get the side


PROMPT_IDENTIFY_IRQ_SIDE = """You are given OCR text extracted from an identity document. Produce a single JSON object that matches this Pydantic model exactly:

IdentifySideResponse:
- is_valid_id: "True" or "" (empty string)
- side: "front", "back", or "" (empty string)

Decision rules:
- Set is_valid_id = "True" if the OCR clearly belongs to an Iraqi National ID (contains Arabic/Kurdish phrases such as "جمهورية العراق", "وزارة الداخلية", "مديرية الأحوال المدنية", Kurdish equivalents, or clear ID structure like MRZ, DOB/issue/expiry dates, or a plausible Iraqi ID number). Otherwise set "".
- Determine side:
  - "back" if OCR includes MRZ (three MRZ lines or MRZ-like patterns with '<'), or contains dates (DOB/issue/expiry) or MRZ-style date fields.
  - "front" if OCR contains personal name fields, ID number, national symbols/text but no dates or MRZ.
  - "" if you cannot confidently classify.
- Use exact string values ("True", "", "front", "back") and nothing else.
- Output only the JSON object (no explanation, no extra keys, no surrounding text).

Examples:
Input OCR:
"@@@\nI<IRQ<<<<DOE<<JOHN<<<<<<<<<<<<\n123456789IRQ\nDOB 01/02/1990\nEXP 01/02/2030\nوزارة الداخلية\n"
Output:
{"is_valid_id":"True","side":"back"}

Input OCR:
"جمهورية العراق\nالاسم: محمد احمد\nالرقم الوطني: 123456789\n"
Output:
{"is_valid_id":"True","side":"front"}

If uncertain about validity or side, prefer empty strings rather than guessing. Return only JSON object"""

PROMPT_FRONT_IRQ = """
Extract ALL fields from this IRAQI National ID Card **front side** image with high accuracy.

1. Extract:
   - First Name in Arabic (`name_ar`) exactly as printed
   - First Name transliterated into English (`name`)
   - Father Name in Arabic (`father_name_ar`) exactly as printed
   - Father Name transliterated into English (`father_name`)
   - Paternal Grandfather Name in Arabic (`third_name_ar`) exactly as printed
   - Paternal Grandfather Name transliterated into English (`third_name`)
   - Family/Tribal Name in Arabic (`family_name_ar`) exactly as printed
   - Family/Tribal Name transliterated into English (`family_name`)
        - If no Family/Tribal Name exists, return `null` for family_name and family_name_ar
   - Mother First Name in Arabic (`mother_first_name_ar`) exactly as printed
   - Mother First Name transliterated into English (`mother_first_name`)
   - Mother Last Name in Arabic (`mother_first_name_ar`) exactly as printed
   - Mother Last Name transliterated into English (`mother_first_name`)

2. Extract:
    - `gender_ar`: return `ذكر ` or `أنثى`
    - `gender_en`: transliterate gender to English as `male` or `female`

3. Extract:
   - `id_number`: exactly 12 digits as printed (do not alter)
   - `card number`: exactly 9-character string as printed (do not alter)
   - `serial_number`: optionally exactly 6-character string as printed (do not alter)
   - `blood_type`: optionally Blood Type as printed (e.g., `O+`, `A-`, etc.)


4. Do NOT guess or hallucinate any values. If unclear, return empty string.

5. Return structured JSON output as per schema only.
"""

PROMPT_BACK_IRQ = """
You are an expert in reading Iraqi National ID Cards. Extract the following fields from the **back side** of the ID image.

1. **Extract MRZ lines (Machine Readable Zone):**
   - Each line must be exactly 30 characters.
   - Return as a list of exactly 3 strings (`mrz`), in order.
   - Keep each line exactly as printed (no padding, no fixing).
   - Remove all whitespace and punctuation.
   - Return exact number of '<' characters in each line of mrz.

2. **Verify IDIRQ prefix:**
   - If the first line of MRZ starts with 'IDIRQ', return `idirq_verified` as true. Otherwise, false.


3. **Extract and format these fields:**
   - `dob_back`, `issue_date`, `expiry_date` in **DD/MM/YYYY** format.

4. **Extract issuing authority:**
    - `issuing_authority_ar`: Issuing authority (جهة الاصدار / لايانى ددرجوون) in Arabic, exactly as printed.
    - `'issuing_authority_en'`: TRANSLATED name of the issuing authority (`issuing_authority_ar`) in English.

5. **Extract place of birth:**
    - `place_of_birth_ar`: Place of birth in Arabic as printed on the back
    - `place_of_birth_en`: Transliterated place of birth (`place_of_birth_ar) into English

6. **Extract Names**
    - `first_name_back`: First name extracted from MRZ line 3, after the '<<' seperator." 
    - `last_name_back`: Surname extracted from MRZ line 3, before the '<<' separator." If this is not present, return null.

7. **Extract Family Number:**
    - `family_number`: 18-character alphanumeric Family number (الرقم العائلي / ژمارەى خێزانی)' exactly as printed (do not alter).

8. **Extract Nationality:**
    - `nationality`: 3-letter ISO nationality code, (e.g. IRQ for Iraq).

8. **DO NOT GUESS.**
   - If a field is faint, blurry, or unclear, return empty string.

9. Return output as JSON according to the defined schema.
"""


PROMPT_PASSPORT_IRQ = """
Extract ALL fields from this Iraqi Passport image with high accuracy.

1. Extract name English:
   - `full_name`: Full Name, in English, exactly as printed
        - Do not add anything from the field 'Surname' into this.
   - `last_name`: Surname, in English, exactly as printed
   - `mother_name`: Mother's full name in English, exactly as printed

2. **Extract place of birth:** 
    - If value of Place of Birth is in English, return exactly as printed.
    - else, if it is not in English, look at the right-hand side of the passport, where it says "Place of Birth"
        - Transliterate this place of birth into English, if it is only in Arabic.
3. Parse and extract:
   - `issuing_authority`, exactly as printed in English.
        - Transliterate `issuing_authority` to English if it is only in Arabic.
   - `issuing_country`: country of issuance or country code, exactly as printed in English.
   - `gender`: Gender/Sex either as Male or Female
   - `dob`, `issue_date`, `expiry_date` → all in DD/MM/YYYY format
   - `id_number`: must be 9-character alphanumeric passport number.
   - `nationality`: use 3-letter ISO format (e.g., IRQ for Iraq, JOR for Jordan)

4. If only two locations are visible, assign the first to place_of_birth and second to issuing_authority.

5. Ensure that the fields `mrz1` and `mrz2` strictly follow the below format for passports:

    - Both `mrz1` and `mrz2` must be exactly 44 characters long.
    - Use the `<` symbol for padding, **not spaces or any other characters**.
    - There should be **no commas, no spaces**, and only uppercase English alphabets, digits, and `<` characters are allowed.
    - If the line is shorter than 44 characters, pad it **only with `<` symbols at the end**, **except**:
        - In `mrz2`, the final character is a **check digit** (usually numeric) and must remain the last character. Padding with `<` should be applied **before** this digit.
    - Do not introduce extra characters to make the string 44 characters. Do not insert `<` between letters or numbers — only at the end (or just before the check digit in `mrz2`).
    - Do not append any punctuation like commas, periods, or symbols.

    Return the lines exactly as shown, with **no trailing whitespace** or formatting.

5. Do not guess or invent any value. If a field is unclear or missing, return empty string.

6. Output MUST be a structured JSON following the defined schema.
"""

class IraqiIDCardFront(BaseModel):
    first_name: str = Field(..., description="First name (الاسم / ناو) in Arabic.")
    first_name_en: str = Field(..., description="Transliterate First name (الاسم / ناو), to English.")
    father_name: str = Field(..., description="Father's name (الأب / باوك) in Arabic.")
    father_name_en: str = Field(..., description="Transliterate Father's name (الأب / باوك) to English.")
    third_name: str = Field(..., description="Paternal grandfather's name (الجد / بابير) in Arabic.")
    third_name_en: str = Field(..., description="Transliterate Paternal grandfather's name (الجد / بابير) to English.")
    last_name: Optional[str] = Field(
        "",
        description=(
            "Family/tribal name (اللقب / نازناو) in Arabic. "
            "OCR extracts various versions of 'نازناو' like الزناو, الزنار; do not interpret them as the family name."
        )
    )
    last_name_en: Optional[str] = Field(
        "",
        description=(
            "Transliterate Family/tribal name (اللقب / نازناو) to English. "
            "OCR extracts various versions of 'نازناو' like الزناو, الزنار; do not interpret them as the family name."
        )
    )
    mother_first_name: str = Field(..., description="Mother's name (الام/ دابك) in Arabic.")
    mother_first_name_en: str = Field(..., description="Transliterate Mother's name (الام/ دابك) to English.")
    mother_last_name: str = Field(..., description="Maternal grandfather's name (الجد / بابير) in Arabic.")
    mother_last_name_en: str = Field(...,
                                     description="Transliterate Maternal grandfather's name (الجد / بابير) to English.")
    gender_ar: str = Field(..., description="Gender (الجنس / ردگار): ذكر (male) or أنثى (female).")
    gender: str = Field(..., description="Translate Gender (الجنس / ردگار) to English")
    id_number: str = Field(..., description="12-digit national ID number.")
    card_number: str = Field(..., description="9-character alphanumeric document number.")
    serial_number: Optional[str] = Field("", description="6-digit card serial number.")
    blood_type: Optional[str] = Field(None, description="Blood type (e.g., O+, A-).")
   


class IraqiIDCardBack(BaseModel):
    issuing_authority_ar: str = Field(..., description="Issuing authority (جهة الاصدار / لايانى ددرجوون) in Arabic")
    issuing_authority_en: str = Field(..., description="TRANSLATE Issuing authority into English")
    issue_date: str = Field(..., description="Issue date in DD/MM/YYYY format")
    expiry_date: str = Field(..., description="Expiry date in DD/MM/YYYY format")
    place_of_birth_ar: str = Field(..., description="Place of birth in Arabic.")
    place_of_birth_en: str = Field(..., description="Transliterated Place of birth into English.")
    dob: str = Field(..., description="Date of birth in DD/MM/YYYY format")
    family_number: str = Field(...,
                               description='18-character alphanumeric Family number (الرقم العائلي / ژمارەى خێزانی) exactly as printed (do not alter).')
    mrz: List[str] = Field(..., min_items=3, max_items=3,
                           description="List of 3 MRZ lines. Each line must be exactly as printed on the ID (30 characters, unaltered).")
    first_name_back: str = Field(..., description="Given name extracted from MRZ line 3, after the '<<' seperator.")
    last_name_back: Optional[str] = Field(...,
                                          description="Surname extracted from MRZ line 3, before the '<<' separator. If this is not present, return null.")
    idirq_verified: bool = Field(..., description="True if the first MRZ line starts with 'IDIRQ'")
    nationality: str = Field(..., description="3-letter nationality code (e.g., IRQ for Iraq)")

    @validator("idirq_verified", always=True)
    def check_idirq(cls, v, values):
        mrz = values.get("mrz", [])
        return bool(mrz and mrz[0].startswith("IDIRQ"))


class IraqiPassport(BaseModel):
    full_name: str = Field(..., description="The Full Name, in English, exactly as printed on the document")
    last_name: str = Field(..., description="Surname of the person on the passport")
    place_of_birth: str = Field(..., description=("If Place of Birth is in English, return exactly as printed."
                                                  "If not present in English, look at the right-hand side of the passport, where it says 'Place of Birth'."
                                                  "Transliterate to English if value of Place of Birth is only in Arabic"))

    issuing_authority: str = Field(..., description=("Place of passport issuance in English"
                                                     "Transliterate to English if issuing authority is only in Arabic"))
    issuing_country: str = Field(..., description="Issuing Country/Country Code (e.g. 'IRQ', 'JOR')", example='IRQ')
    mother_name: str = Field(..., description="Mother's full name in English, exactly as printed.")
    gender: str = Field(..., description="printed as Sex: M or F return 'Male' or 'Female' accordingly")
    mrz1: str = Field(..., min_length=44, max_length=44,
                      description="First line of the MRZ, exactly 44 characters, padded with '<' at the end if shorter")
    mrz2: str = Field(..., min_length=44, max_length=44,
                      description="Second line of the MRZ, exactly 44 characters. Padding with '<' must be inserted before the final check digit.")
    id_number: str = Field(..., pattern=r"^[A-Z][0-9]{8}$",
                           description="Passport number: one uppercase letter followed by 8 digits")

    dob: str = Field(
        ..., description="Date of birth in DD/MM/YYYY format"
    )
    issue_date: str = Field(
        ..., description="Issue date in DD/MM/YYYY format"
    )
    expiry_date: str = Field(
        ..., description="Expiry date in DD/MM/YYYY format"
    )
    nationality: str = Field(
        ..., description="Nationality in ISO 3166-1 alpha-3 format (e.g., SDN)"
    )

    header_verified: bool = Field(
        ..., description="True if document header ('IRQ', 'Republic of Iraq') is detected"
    )

class IdentifyIRQSideResponse(BaseModel):
    is_valid_id: bool = Field(..., description="Return True if document is either a valid Iraqi National ID's front side or back side." 
            "It should contain Arabic/Kurdish text like: جمهورية العراق / وزارة الداخلية"
            "مديرية الأحوال المدنية والجوازات والاقامة"
            "کوماری عیراق / وه زاره تی ناوخو"
            "پریود به را بائی باری شارستانی و پاسپورت و نیشنگه"
            "جمهورية العراق / وزارة الداخلية"
            "کوماری عیراق / وه زاره تی ناوخو"
            "Return empty string '' otherwise.")
#    side should be one of the front, back or empty string
    side: str = Field(..., description="Determine  if this is a front side or back side of an Iraqi National ID. Return empty string if its neither."
                                             "A back side has three lines of MRZ, has dates of birth, issue and expiry"
                                             "A front side has names, and id number. No dates. return front or back accordingly.")



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

def get_irq_side_from_openai(image, openai_key):

    logging.info(f"Getting side of Iraqi ID from OpenAI... and type of image {type(image)}")
    base_64_image = _image_to_jpeg_bytesio(image)
    b64_image = base64.b64encode(base_64_image.getvalue()).decode("utf-8")

    logging.info(f"Converted image to JPEG BytesIO for OpenAI processing. type of base_64_image {type(b64_image)}")
    for attempt in range(3):
        try:
            client = OpenAI(api_key=openai_key)
            # image_data = base64.b64decode(b64_image)
            response = client.responses.parse(
                model="gpt-4.1-mini",
                input = [{"role": "system", "content": "You are an expert at extracting information from identity documents, extract data as per fields, dont use any additional text or infer from mrz data."},
                    {"role": "user", "content": [
                        {"type": "input_text", "text": PROMPT_IDENTIFY_IRQ_SIDE},
                        {"type": "input_image", "image_url": f"data:image/jpeg;base64,{b64_image}", "detail": "low"},
                    ]},
                ],
                text_format = IdentifyIRQSideResponse
            )
            logging.info(f"Received response from OpenAI for side identification., {response.output_parsed}")
             
            return vars(response.output_parsed)
        
        except Exception as e:
            logging.error(f"Error in get_side_from_openAI attempt {attempt + 1}: {e}")
            time.sleep(2)
    return {"is_valid_id": "", "side": ""}, b64_image

def get_openai_response_irq(prompt: str, model_type, image: BytesIO, genai_key):

    for attempt in range(3):
        try:
            client = OpenAI(api_key=genai_key)
            response = client.responses.parse(
                model="gpt-4.1-mini",
                input=[
                    {"role": "system",
                     "content": "You are an expert at extracting information from identity documents."},
                    {"role": "user", "content": [
                        {"type": "input_text", "text": prompt},
                        {"type": "input_image", "image_url": f"data:image/jpeg;base64,{image}", "detail": "low"},
                    ]},
                ],
                text_format=model_type,
            )
            return response.output_parsed
        except Exception as e:
            logging.info(f"[ERROR] Attempt {attempt + 1} failed: {str(e)}")
            time.sleep(2)
    return None

def process_image_irq(side):
    if side == "front":
        prompt = PROMPT_FRONT_IRQ
        model = IraqiIDCardFront

    elif side == "back":
        prompt = PROMPT_BACK_IRQ
        model = IraqiIDCardBack

    elif side == "passport":
        prompt = PROMPT_PASSPORT_IRQ
        model = IraqiPassport
    else:
        raise ValueError("Invalid document side specified. Use 'front', 'back', or 'passport'.")

    return model, prompt

def get_response_from_openai_irq(image, side, openai_key):
    logging.info(f"Getting response from OpenAI for Iraqi Id side {side}... and type of image {type(image)}")
    try:
        base_64_image = _image_to_jpeg_bytesio(image)
        b64_image = base64.b64encode(base_64_image.getvalue()).decode("utf-8")
        logging.info(f"Converted image to JPEG BytesIO for OpenAI processing. type of base_64_image {type(b64_image)}")
    except Exception as e:
        logging.error(f"Error converting image: {e}")
        return {"error": "Image conversion failed"}
    try:
        model, prompt = process_image_irq(side)
        logging.info(f"Using model: {model.__name__} and prompt {prompt[:100]}")
    except ValueError as ve:
        logging.error(f"Error: {ve}")
        return {"error": str(ve)}

    try:
        response = get_openai_response_irq(prompt, model, b64_image, openai_key)
    except Exception as e:
        logging.error(f"Error during OpenAI request: {e}")
        return {"error": "OpenAI request failed"}

    response_data = vars(response)
    logging.info(f"Openai response: {response}")
    return response_data