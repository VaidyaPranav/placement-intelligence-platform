from pathlib import Path
import sys
from pypdf import PdfReader
import traceback

# Ensure backend root is on sys.path so `app` package can be imported when
# running this script from the `tests/` folder.
ROOT = Path(__file__).resolve().parent
BACKEND_ROOT = ROOT.parent
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from app.agents.student_agent.agent import extract_student_profile

print("=" * 80)
print("STARTING STUDENT AGENT PDF TEST")
print("=" * 80)

try:
    # Path to resume PDF
    pdf_path = Path("resume.pdf")

    if not pdf_path.exists():
        raise FileNotFoundError(f"Resume PDF not found: {pdf_path}")

    # Extract text from PDF
    reader = PdfReader(str(pdf_path))

    resume_text = ""

    for page in reader.pages:
        page_text = page.extract_text()

        if page_text:
            resume_text += page_text + "\n"

    print("\nPDF TEXT EXTRACTION COMPLETE")
    print("Characters Extracted:", len(resume_text))

    print("\nFIRST 500 CHARACTERS:")
    print("-" * 50)
    print(resume_text[:500])
    print("-" * 50)

    # Run Student Intelligence Agent
    result = extract_student_profile(
        student_id="11111111-1111-4111-8111-111111111111",
        resume_text=resume_text
    )

    print("\nSTUDENT PROFILE GENERATED")
    print("=" * 80)

    print(result.model_dump_json(indent=2))

except Exception as e:
    print("\nERROR OCCURRED")
    print("=" * 80)

    print("ERROR TYPE:")
    print(type(e))

    print("\nERROR MESSAGE:")
    print(str(e))

    print("\nTRACEBACK:")
    traceback.print_exc()

print("\n")
print("=" * 80)
print("TEST FINISHED")
print("=" * 80)