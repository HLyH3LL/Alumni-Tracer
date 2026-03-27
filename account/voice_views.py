# views.py
import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

@require_POST
def voice_update(request):
    """
    Handles uploaded audio for Alumni Tracer.
    Receives audio file and form type, processes it,
    and returns extracted data as JSON.
    """
    audio_file = request.FILES.get('audio')
    form_type = request.POST.get('form_type', 'unknown')

    if not audio_file:
        return JsonResponse({
            'success': False,
            'message': 'No audio file uploaded.'
        })

    try:
        # Example: Save uploaded audio to a temporary location
        # You can replace this with processing logic (speech-to-text, etc.)
        save_path = f'media/voice_uploads/{audio_file.name}'
        with open(save_path, 'wb+') as f:
            for chunk in audio_file.chunks():
                f.write(chunk)

        # Dummy example of extracted data
        # In reality, you could run speech-to-text or AI processing here
        extracted_data = {}
        if form_type == 'employment':
            extracted_data = {
                'company_name': 'ABC Corp',
                'position': 'Software Engineer',
                'start_date': '2023-06-01',
                'end_date': '2025-03-23'
            }
        elif form_type == 'study':
            extracted_data = {
                'school_name': 'University of XYZ',
                'degree': 'Bachelor of IT',
                'year_graduated': '2023'
            }

        return JsonResponse({
            'success': True,
            'message': 'Voice processed successfully!',
            'extracted_data': extracted_data
        })

    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Error processing audio: {str(e)}'
        })