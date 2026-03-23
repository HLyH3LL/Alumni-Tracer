/**
 * Voice Recorder Module
 * Handles audio recording, playback, and upload for Alumni Tracer
 * 
 * Features:
 * - Record audio using Web Audio API
 * - Real-time audio visualization
 * - Upload audio to backend for processing
 * - Handle loading and error states
 */

class VoiceRecorder {
    constructor(config = {}) {
        this.mediaRecorder = null;
        this.audioChunks = [];
        this.isRecording = false;
        this.recordButton = config.recordButton || document.getElementById('voice-record-btn');
        this.stopButton = config.stopButton || document.getElementById('voice-stop-btn');
        this.playButton = config.playButton || document.getElementById('voice-play-btn');
        this.uploadButton = config.uploadButton || document.getElementById('voice-upload-btn');
        this.statusElement = config.statusElement || document.getElementById('voice-status');
        this.progressBar = config.progressBar || document.getElementById('recording-progress');
        this.formType = config.formType || 'employment'; // 'employment' or 'study'
        this.audioBlob = null;
        this.stream = null;
        this.recordingStartTime = null;
        this.recordingDuration = 0;
        this.timerInterval = null;
        
        this.init();
    }

    init() {
        console.log('🎙️ Voice Recorder initialized');
        this.attachEventListeners();
    }

    attachEventListeners() {
        if (this.recordButton) {
            this.recordButton.addEventListener('click', () => this.startRecording());
        }
        if (this.stopButton) {
            this.stopButton.addEventListener('click', () => this.stopRecording());
        }
        if (this.playButton) {
            this.playButton.addEventListener('click', () => this.playRecording());
        }
        if (this.uploadButton) {
            this.uploadButton.addEventListener('click', () => this.uploadRecording());
        }
    }

    async startRecording() {
        try {
            console.log('🎙️ Starting recording...');
            
            // Request microphone access
            this.stream = await navigator.mediaDevices.getUserMedia({ 
                audio: {
                    echoCancellation: true,
                    noiseSuppression: true,
                    autoGainControl: true
                }
            });
            
            // Create MediaRecorder
            this.mediaRecorder = new MediaRecorder(this.stream, {
                mimeType: 'audio/webm;codecs=opus'
            });
            
            this.audioChunks = [];
            this.recordingStartTime = Date.now();
            this.recordingDuration = 0;
            this.isRecording = true;
            
            // Event: when audio data becomes available
            this.mediaRecorder.ondataavailable = (event) => {
                this.audioChunks.push(event.data);
            };
            
            // Event: when recording stops
            this.mediaRecorder.onstop = () => {
                this.audioBlob = new Blob(this.audioChunks, { type: 'audio/webm' });
                console.log('✅ Recording stopped. Audio blob size:', this.audioBlob.size);
                this.updateStatus('✅ Recording saved. Ready to upload or replay.', 'success');
            };
            
            this.mediaRecorder.start();
            this.updateRecordingUI();
            this.startTimer();
            this.updateStatus('🎙️ Recording... Click "Stop" when done.', 'recording');
            
        } catch (error) {
            console.error('❌ Error accessing microphone:', error);
            this.updateStatus('❌ Microphone access denied. Please enable it in your browser settings.', 'error');
        }
    }

    stopRecording() {
        if (!this.mediaRecorder || !this.isRecording) {
            console.warn('No recording in progress');
            return;
        }
        
        console.log('⏹️ Stopping recording...');
        this.mediaRecorder.stop();
        
        // Stop all audio tracks
        if (this.stream) {
            this.stream.getTracks().forEach(track => track.stop());
        }
        
        this.isRecording = false;
        this.stopTimer();
        this.updateRecordingUI();
    }

    playRecording() {
        if (!this.audioBlob) {
            this.updateStatus('❌ No recording available to play.', 'error');
            return;
        }
        
        console.log('▶️ Playing recording...');
        const audioUrl = URL.createObjectURL(this.audioBlob);
        const audio = new Audio(audioUrl);
        audio.play();
        this.updateStatus('▶️ Playing recording...', 'info');
    }

    async uploadRecording() {
        if (!this.audioBlob) {
            this.updateStatus('❌ No recording to upload.', 'error');
            return;
        }

        const formData = new FormData();
        formData.append('audio', this.audioBlob, 'recording.webm');
        formData.append('form_type', this.formType);
        formData.append('csrfmiddlewaretoken', this.getCSRFToken());

        try {
            this.updateStatus('⏳ Processing voice... This may take a few seconds.', 'loading');
            this.uploadButton.disabled = true;
            this.uploadButton.innerHTML = '<span class="spinner"></span> Processing...';

            const response = await fetch('/account/voice-update/', {
                method: 'POST',
                body: formData,
                headers: {
                    'X-Requested-With': 'XMLHttpRequest'
                }
            });

            const data = await response.json();

            if (response.ok && data.success) {
                console.log('✅ Voice update successful:', data);
                this.updateStatus('✅ ' + data.message, 'success');
                this.showExtractedData(data.extracted_data);
                
                // Auto-fill form with extracted data
                if (data.extracted_data) {
                    this.populateForm(data.extracted_data);
                }
                
                // Clear recording
                setTimeout(() => this.clearRecording(), 2000);
            } else {
                console.error('❌ Error:', data.message || 'Unknown error');
                this.updateStatus('❌ ' + (data.message || 'Failed to process voice'), 'error');
            }
        } catch (error) {
            console.error('❌ Upload error:', error);
            this.updateStatus('❌ Upload failed: ' + error.message, 'error');
        } finally {
            this.uploadButton.disabled = false;
            this.uploadButton.innerHTML = '<i class="fas fa-microphone"></i> Upload Voice';
        }
    }

    populateForm(data) {
        console.log('📝 Populating form with:', data);
        
        for (const [fieldName, fieldValue] of Object.entries(data)) {
            const input = document.querySelector(`[name="${fieldName}"]`);
            if (input) {
                if (input.type === 'checkbox') {
                    input.checked = fieldValue === true || fieldValue === 'true';
                } else if (input.tagName === 'SELECT') {
                    input.value = fieldValue;
                } else {
                    input.value = fieldValue;
                }
                
                // Trigger change event for validation
                input.dispatchEvent(new Event('change', { bubbles: true }));
                console.log(`✅ Set ${fieldName} to ${fieldValue}`);
            }
        }
    }

    showExtractedData(data) {
        if (!data) return;
        
        let html = '<div class="extracted-data-preview" style="margin-top: 15px; padding: 15px; background: rgba(76, 175, 80, 0.1); border: 1px solid #4caf50; border-radius: 8px;">';
        html += '<h4 style="color: #4caf50; margin-bottom: 10px;">📋 Extracted Information:</h4>';
        html += '<ul style="list-style: none; padding: 0; margin: 0;">';
        
        for (const [key, value] of Object.entries(data)) {
            if (value) {
                const displayKey = key.replace(/_/g, ' ').toUpperCase();
                html += `<li style="padding: 5px 0; color: rgba(255, 255, 255, 0.9);">
                    <strong>${displayKey}:</strong> ${value}
                </li>`;
            }
        }
        
        html += '</ul></div>';
        
        const statusElement = this.statusElement;
        if (statusElement) {
            statusElement.insertAdjacentHTML('afterend', html);
            
            // Remove after 10 seconds
            setTimeout(() => {
                const preview = document.querySelector('.extracted-data-preview');
                if (preview) preview.remove();
            }, 10000);
        }
    }

    startTimer() {
        this.recordingStartTime = Date.now();
        this.timerInterval = setInterval(() => {
            this.recordingDuration = Math.floor((Date.now() - this.recordingStartTime) / 1000);
            const minutes = Math.floor(this.recordingDuration / 60);
            const seconds = this.recordingDuration % 60;
            const displayTime = `${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`;
            
            if (this.recordButton) {
                this.recordButton.textContent = `Recording... ${displayTime}`;
            }
        }, 100);
    }

    stopTimer() {
        if (this.timerInterval) {
            clearInterval(this.timerInterval);
        }
    }

    updateRecordingUI() {
        if (this.isRecording) {
            if (this.recordButton) {
                this.recordButton.disabled = true;
                this.recordButton.style.opacity = '0.5';
            }
            if (this.stopButton) {
                this.stopButton.disabled = false;
                this.stopButton.style.opacity = '1';
            }
        } else {
            if (this.recordButton) {
                this.recordButton.disabled = false;
                this.recordButton.style.opacity = '1';
                this.recordButton.innerHTML = '<i class="fas fa-microphone"></i> Record Voice';
            }
            if (this.stopButton) {
                this.stopButton.disabled = true;
                this.stopButton.style.opacity = '0.5';
            }
            if (this.playButton && this.audioBlob) {
                this.playButton.disabled = false;
                this.playButton.style.opacity = '1';
            }
            if (this.uploadButton && this.audioBlob) {
                this.uploadButton.disabled = false;
                this.uploadButton.style.opacity = '1';
            }
        }
    }

    updateStatus(message, type = 'info') {
        if (!this.statusElement) return;
        
        const typeClass = `alert-${type}`;
        const iconMap = {
            'recording': 'fas fa-microphone',
            'loading': 'fas fa-spinner',
            'success': 'fas fa-check-circle',
            'error': 'fas fa-exclamation-circle',
            'info': 'fas fa-info-circle'
        };
        
        this.statusElement.innerHTML = `
            <i class="fas ${iconMap[type] || iconMap['info']}"></i>
            <span>${message}</span>
        `;
        this.statusElement.className = `alert ${typeClass}`;
        this.statusElement.style.display = 'flex';
    }

    clearRecording() {
        this.audioBlob = null;
        this.audioChunks = [];
        this.recordingDuration = 0;
        this.updateRecordingUI();
        this.updateStatus('🎙️ Ready to record. Click "Record Voice" to start.', 'info');
    }

    getCSRFToken() {
        return document.querySelector('[name=csrfmiddlewaretoken]')?.value || '';
    }
}

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', function() {
    // Check if we're on a form page
    const formType = document.body.getAttribute('data-form-type');
    if (formType) {
        window.voiceRecorder = new VoiceRecorder({
            formType: formType
        });
        console.log('✅ Voice Recorder ready for', formType, 'form');
    }
});