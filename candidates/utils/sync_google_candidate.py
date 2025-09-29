from django.db import IntegrityError
import phonenumbers
from ..models import CandidateInitialInformation, SpreadSheetTracker
from jobs.models import Job
from .google_sheet_Candidates import CandidateGoogleSheet
from ..views import Resume_Date_As_JSON
from .text_converter import TextConverter
import logging

TestConverter = TextConverter()
logger = logging.getLogger(__name__)

def Candidate_GoogleSheet_Data(sheet_id):
    # Fetch the Job object (only open jobs with Google Sheet ID)
    try:
        jobs = Job.objects.filter(google_sheet_id=sheet_id, open_status=True)
    except Job.DoesNotExist:
        return "No open job with Google Sheet ID found."

    job = jobs.first()
    # Get or create last_row tracker for this sheet
    obj, created = SpreadSheetTracker.objects.get_or_create(
        sheet_id=jobs.first().google_sheet_id, defaults={"last_row": 1}
    )
    last_row = obj.last_row

    # Fetch candidate data starting from last_row
    candidateInfo = CandidateGoogleSheet().get_candidate_data_google_sheet(
        spreadsheet_id=jobs.first().google_sheet_id, last_row=last_row
    )
    
    

    for data in candidateInfo:
        try:
            # Format mobile number
            try:
                formatted_mobile = phonenumbers.parse(data["Mobile No."], "BD")
                data["Mobile No."] = phonenumbers.format_number(
                    formatted_mobile, phonenumbers.PhoneNumberFormat.E164
                )
            except phonenumbers.phonenumberutil.NumberParseException:
                continue
            
            name = (data.get('Name') or "").strip()
            if not name:
                logger.warning(f"Skipping row {last_row + 1} — missing Name")
                continue  # skip row if name is empty

            exists = CandidateInitialInformation.objects.filter(
                name=name.title(),
                mobile_no=data["Mobile No."],
                jobs=job
            ).exists()
            # Check for duplicate candidate
            file_id = data['Upload Your Resume'].split("=", 1)[1]
            # Create candidate if not duplicate
            if not exists:
                candidate = CandidateInitialInformation(
                    name=name.title(),
                    mobile_no=data["Mobile No."],
                    email=data.get('Email', ''),
                    current_designation=data.get('Current Position', ''),
                    current_organization=data.get('Current Organization', ''),
                    current_location=data.get('Current Location (Work Place)', ''),
                    total_experience=data.get('Total Experience (Years)', ''),
                    resume=CandidateGoogleSheet().download_resume(file_id=file_id))
                candidate.save()
                candidate.jobs.add(*jobs)
                
                # Extract resume data
                try:
                    if candidate.resume.path.endswith(".pdf"):
                        extracted_text = TextConverter.pdf_to_text(
                            candidate.resume.path
                        )
                    elif candidate.resume.path.endswith(".doc"):
                        extracted_text = TextConverter.doc_to_text(
                            candidate.resume.path
                        )
                    elif candidate.resume.path.endswith(".docx"):
                        extracted_text = TextConverter.docx_to_text(
                            candidate.resume.path
                        )
                    elif (
                        candidate.resume.path.endswith(".jpg")
                        or candidate.resume.path.endswith(".jpeg")
                        or candidate.resume.path.endswith(".png")
                    ):
                        extracted_text = TextConverter.img_to_text(
                            candidate.resume.path
                        )
                    else:
                        raise ValueError("Unsupported file format")
                except Exception as e:
                    logging.error(f"Error extracting text from file: {e}")
                    raise

                extracted_text = TextConverter.pdf_to_text(candidate.resume.path)
                response = Resume_Date_As_JSON("\n".join(extracted_text))
                candidate.highest_education_degree = response.get("Highest_Educational_Degree")
                candidate.highest_education_degree_institution = response.get("Highest_Education_Degree_Institution")
                candidate.passing_year = response.get("Passing_Year")
                candidate.professional_education_degree = response.get("Professional_Degree")
                candidate.experience = response.get("Experience")
                candidate.address = response.get("Permanent_Address")
                candidate.save()
            else:
                print(f"Duplicate found: {data['Name']}, {data['Mobile No.']}")

        except Exception as e:
            print(f"{e} on row {last_row + 1}")
            continue

        finally:
            # Increment last_row after processing each entry
            last_row += 1

    # Update last_row tracker in DB
    obj.last_row = last_row
    obj.save()

    return "Sync completed successfully."
