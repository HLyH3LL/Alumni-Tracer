# views.py
import json
import os
import re
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.conf import settings

# Try to load environment variables (optional)
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass  # dotenv not installed, continue without it

def get_openai_client():
    """Get OpenAI client with API key check"""
    try:
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            return None
        from openai import OpenAI
        return OpenAI(api_key=api_key)
    except ImportError:
        return None

@require_POST
@csrf_exempt  # Remove this in production and handle CSRF properly
def voice_update(request):
    """
    Handles uploaded audio for Alumni Tracer.
    Currently returns dummy data. To make functional, install required packages
    and set OPENAI_API_KEY in .env file.
    """
    audio_file = request.FILES.get('audio')
    form_type = request.POST.get('form_type', 'unknown')

    if not audio_file:
        return JsonResponse({
            'success': False,
            'message': 'No audio file uploaded.'
        })

    try:
        # Create voice_uploads directory if it doesn't exist
        upload_dir = os.path.join(settings.MEDIA_ROOT, 'voice_uploads')
        os.makedirs(upload_dir, exist_ok=True)

        # Save uploaded audio
        file_path = os.path.join(upload_dir, audio_file.name)
        with open(file_path, 'wb+') as f:
            for chunk in audio_file.chunks():
                f.write(chunk)

        # Check if OpenAI is available and configured
        client = get_openai_client()
        if client and os.getenv('OPENAI_API_KEY'):
            try:
                # Transcribe audio using OpenAI Whisper
                with open(file_path, 'rb') as audio:
                    transcript_response = client.audio.transcriptions.create(
                        model="whisper-1",
                        file=audio,
                        response_format="text"
                    )

                transcript = transcript_response.strip()

                # Extract structured data based on form type
                extracted_data = extract_data_from_transcript(transcript, form_type, client)

            except Exception as e:
                # Fallback to dummy data if API fails
                transcript = f"Audio uploaded but transcription failed: {str(e)}"
                extracted_data = get_dummy_data(form_type)
        else:
            # No API key or OpenAI not available - use dummy data
            transcript = f"Audio file '{audio_file.name}' uploaded successfully. Install OpenAI API key and packages for real transcription."
            extracted_data = get_dummy_data(form_type)

        return JsonResponse({
            'success': True,
            'message': f'Voice processed successfully for {form_type} form!',
            'extracted_data': extracted_data,
            'transcript': transcript,
            'audio_file': audio_file.name
        })

    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Error processing audio: {str(e)}'
        })

def get_dummy_data(form_type):
    """Return dummy data based on form type"""
    if form_type == 'employment':
        return {
            'company_name': 'Example Company',
            'job_title': 'Software Developer',
            'date_hired': '2023-01-15',
            'employment_type': 'FULL_TIME',
            'is_job_related': True
        }
    elif form_type == 'study':
        return {
            'school_name': 'Example University',
            'program': 'Computer Science',
            'start_year': '2020',
            'end_year': '2024',
            'status': 'COMPLETED'
        }
    return {}

def extract_data_from_transcript(transcript, form_type, client):
    """
    Extract structured data from transcript using OpenAI GPT
    This is a placeholder - implement based on your needs
    """
    try:
        prompt = f"""
        Extract the following information from this transcript about {form_type}:

        Transcript: {transcript}

        Return only a JSON object with the relevant fields for {form_type} form.
        """

        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=300
        )

        # Parse the response (this would need proper JSON parsing)
        return get_dummy_data(form_type)  # Placeholder

    except Exception:
        return get_dummy_data(form_type)


def extract_data_from_transcript(transcript, form_type, client=None):
    """
    Extract structured data from transcript using pattern matching and OpenAI GPT.
    """
    if not transcript:
        return {}

    if not client:
        # Fallback to pattern matching if no client
        return fallback_extraction(transcript, form_type)

    # Use GPT-4 to extract structured information
    prompt = f"""
    Extract information from this voice transcript for a {form_type} form.
    Return ONLY a valid JSON object with the appropriate fields.

    Transcript: "{transcript}"

    For employment forms, extract:
    - company_name: Company or organization name
    - job_title: Job title or position
    - date_hired: Start date (YYYY-MM-DD format if mentioned)
    - date_left: End date (YYYY-MM-DD format if mentioned, null if current)
    - employment_type: FULL_TIME, PART_TIME, CONTRACT, FREELANCE, INTERNSHIP, or TEMPORARY
    - is_job_related: true/false if related to their degree

    For study forms, extract:
    - school_name: School or university name
    - program: Program or degree name
    - start_year: Starting year (YYYY format)
    - end_year: Ending year (YYYY format, null if ongoing)
    - status: COMPLETED, ONGOING, DROPPED, or TRANSFERRED
    - is_ongoing: true/false if currently studying

    Return only JSON, no explanation.
    """

    try:
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a helpful assistant that extracts structured data from voice transcripts. Always return valid JSON."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=500,
            temperature=0.1
        )

        result_text = response.choices[0].message.content.strip()

        # Clean up the response to ensure it's valid JSON
        result_text = result_text.replace('```json', '').replace('```', '').strip()

        # Parse the JSON
        extracted_data = json.loads(result_text)

        return extracted_data

    except Exception as e:
        print(f"Error extracting data with GPT: {e}")
        # Fallback to pattern matching
        return fallback_extraction(transcript, form_type)


def fallback_extraction(transcript, form_type):
    """
    Fallback extraction using regex patterns if GPT fails.
    """
    data = {}

    if form_type == 'employment':
        # Simple pattern matching for employment
        company_match = re.search(r'(?:work(?:ed|ing)?(?:\s+at|for)\s+|company\s+|organization\s+|firm\s+)([A-Za-z\s&]+?)(?:\s+(?:as|in|since|from)|\s*$)', transcript, re.IGNORECASE)
        if company_match:
            data['company_name'] = company_match.group(1).strip()

        title_match = re.search(r'(?:as\s+|position\s+|job\s+|role\s+|title\s+)([A-Za-z\s]+?)(?:\s+(?:at|since|from)|\s*$)', transcript, re.IGNORECASE)
        if title_match:
            data['job_title'] = title_match.group(1).strip()

        # Look for dates
        date_patterns = [
            r'(\d{1,2}[-/]\d{1,2}[-/]\d{4})',  # MM/DD/YYYY or DD/MM/YYYY
            r'(\d{4}[-/]\d{1,2}[-/]\d{1,2})',  # YYYY/MM/DD
            r'(?:january|february|march|april|may|june|july|august|september|october|november|december|\d{1,2})(?:\s+\d{1,2})?,?\s+\d{4}', re.IGNORECASE
        ]

        dates = []
        for pattern in date_patterns:
            matches = re.findall(pattern, transcript)
            dates.extend(matches)

        if len(dates) >= 1:
            data['date_hired'] = dates[0]
        if len(dates) >= 2:
            data['date_left'] = dates[1]

    elif form_type == 'study':
        # Simple pattern matching for studies
        school_match = re.search(r'(?:stud(?:y|ied|ying)(?:\s+at)?\s+|university\s+|college\s+|school\s+|institute\s+)([A-Za-z\s&]+?)(?:\s+(?:in|for|since)|\s*$)', transcript, re.IGNORECASE)
        if school_match:
            data['school_name'] = school_match.group(1).strip()

        program_match = re.search(r'(?:degree\s+in|major\s+in|program\s+|course\s+|studying\s+)([A-Za-z\s]+?)(?:\s+(?:at|since|from)|\s*$)', transcript, re.IGNORECASE)
        if program_match:
            data['program'] = program_match.group(1).strip()

        # Look for years
        year_matches = re.findall(r'\b(20\d{2})\b', transcript)
        if len(year_matches) >= 1:
            data['start_year'] = year_matches[0]
        if len(year_matches) >= 2:
            data['end_year'] = year_matches[1]

    return data