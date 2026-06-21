import os
import sys
import traceback
from pathlib import Path

ROOT = Path(__file__).resolve().parent
BACKEND_ROOT = ROOT.parent
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from app.agents.company_agent.agent import extract_hiring_requirements, fallback_regex_parse

req_path = ROOT / 'req.txt'
job_description = req_path.read_text(encoding='utf-8')

print('=' * 80)
print('STARTING COMPANY AGENT TEST')
print('=' * 80)

from app.config import GOOGLE_API_KEY
api_key = GOOGLE_API_KEY

if not api_key:
    print('WARNING: GOOGLE_API_KEY is not set. Using fallback regex parser only.')
    try:
        result = fallback_regex_parse(
            job_id='5dc3041e-17e9-4b4b-bca0-59f607bc2329',
            raw_text=job_description,
            error_msg='Missing API key'
        )
        print('\nFALLBACK RESULT TYPE:')
        print(type(result))
        print('\nFALLBACK RESULT JSON:')
        print(result.model_dump_json(indent=2))
    except Exception as e:
        print('\nERROR OCCURRED IN FALLBACK\n')
        print('ERROR MESSAGE:')
        print(str(e))
        print('\nFULL TRACEBACK:')
        traceback.print_exc()
else:
    try:
        result = extract_hiring_requirements(
            job_id='5dc3041e-17e9-4b4b-bca0-59f607bc2329',
            raw_text=job_description
        )
        print('\nSUCCESS\n')
        print('RESULT TYPE:')
        print(type(result))
        print('\nRESULT JSON:')
        print(result.model_dump_json(indent=2))
    except Exception as e:
        print('\nERROR OCCURRED\n')
        print('ERROR TYPE:')
        print(type(e))
        print('\nERROR MESSAGE:')
        print(str(e))
        print('\nFULL TRACEBACK:')
        traceback.print_exc()

        print('\nFALLING BACK TO REGEX PARSER\n')
        try:
            fallback_result = fallback_regex_parse(
                job_id='5dc3041e-17e9-4b4b-bca0-59f607bc2329',
                raw_text=job_description,
                error_msg=str(e)
            )
            print('FALLBACK RESULT TYPE:')
            print(type(fallback_result))
            print('\nFALLBACK RESULT JSON:')
            print(fallback_result.model_dump_json(indent=2))
        except Exception as fallback_error:
            print('\nERROR OCCURRED IN FALLBACK\n')
            print('ERROR MESSAGE:')
            print(str(fallback_error))
            print('\nFULL TRACEBACK:')
            traceback.print_exc()

print('\n')
print('=' * 80)
print('TEST FINISHED')
print('=' * 80)