
class VoiceRecorder {
    constructor(config = {}) {
        this.mediaRecorder = null;
        this.audioChunks = [];
        this.audioBlob = null;
        this.isRecording = false;
        this.recordButton = config.recordButton || document.getElementById('voice-record-btn');
        this.stopButton = config.stopButton || document.getElementById('voice-stop-btn');
        this.playButton = config.playButton || document.getElementById('voice-play-btn');
        this.uploadButton = config.uploadButton || document.getElementById('voice-upload-btn');
        this.statusElement = config.statusElement || document.getElementById('voice-status');
        this.formType = config.formType || 'employment';
        this.stream = null;
        this.timerInterval = null;
        this.recordingStartTime = null;
        this.recordingDuration = 0;

        this.init();
    }

    init() {
        console.log('Voice Recorder initialized');
        this.attachEventListeners();
        this.updateRecordingUI();
    }

    attachEventListeners() {
        this.recordButton?.addEventListener('click', () => this.startRecording());
        this.stopButton?.addEventListener('click', () => this.stopRecording());
        this.playButton?.addEventListener('click', () => this.playRecording());
        this.uploadButton?.addEventListener('click', () => this.uploadRecording());
    }

    async startRecording() {
        try {
            this.stream = await navigator.mediaDevices.getUserMedia({ audio: true });
            this.mediaRecorder = new MediaRecorder(this.stream, { mimeType: 'audio/webm;codecs=opus' });

            this.audioChunks = [];
            this.mediaRecorder.ondataavailable = (e) => this.audioChunks.push(e.data);
            this.mediaRecorder.onstop = () => {
                this.audioBlob = new Blob(this.audioChunks, { type: 'audio/webm' });
                console.log('Recording saved:', this.audioBlob.size, 'bytes');
                this.updateStatus('Recording saved. Ready to upload or play.', 'success');
                this.updateRecordingUI();
            };

            this.mediaRecorder.start();
            this.isRecording = true;
            this.recordingStartTime = Date.now();
            this.startTimer();
            this.updateStatus('Recording... Click Stop when done.', 'recording');
            this.updateRecordingUI();
        } catch (err) {
            console.error('Microphone error:', err);
            this.updateStatus('Unable to access microphone.', 'error');
        }
    }

    stopRecording() {
        if (!this.isRecording || !this.mediaRecorder) return;

        this.mediaRecorder.stop();
        this.stream?.getTracks().forEach(track => track.stop());
        this.isRecording = false;
        this.stopTimer();
        this.updateRecordingUI();
    }

    playRecording() {
        if (!this.audioBlob) {
            this.updateStatus('No recording to play.', 'error');
            return;
        }
        const audioUrl = URL.createObjectURL(this.audioBlob);
        const audio = new Audio(audioUrl);
        audio.play();
        this.updateStatus('Playing recording...', 'info');
    }

    async uploadRecording() {
        if (!this.audioBlob) {
            this.updateStatus('No recording to upload.', 'error');
            return;
        }

        const formData = new FormData();
        formData.append('audio', this.audioBlob, 'recording.webm');
        formData.append('form_type', this.formType);
        formData.append('csrfmiddlewaretoken', this.getCSRFToken());

        this.uploadButton.disabled = true;
        this.uploadButton.innerHTML = '<span class="spinner"></span> Uploading...';
        this.updateStatus('Uploading...', 'loading');

        try {
            const response = await fetch('/account/voice-update/', {
                method: 'POST',
                body: formData,
                headers: { 'X-Requested-With': 'XMLHttpRequest' }
            });

            const data = await response.json();
            if (response.ok && data.success) {
                console.log('Upload success:', data);
                this.updateStatus((data.message || 'Voice processed successfully'), 'success');
                if (data.extracted_data) this.populateForm(data.extracted_data);
                setTimeout(() => this.clearRecording(), 2000);
            } else {
                console.error('Upload failed:', data);
                this.updateStatus((data.message || 'Upload failed'), 'error');
            }
        } catch (err) {
            console.error('Upload error:', err);
            this.updateStatus('Upload failed: ' + err.message, 'error');
        } finally {
            this.uploadButton.disabled = false;
            this.uploadButton.innerHTML = '<i class="fas fa-microphone"></i> Upload Voice';
        }
    }

    populateForm(data) {
        for (const [key, value] of Object.entries(data)) {
            const input = document.querySelector(`[name="${key}"]`);
            if (!input) continue;
            if (input.type === 'checkbox') input.checked = value === true || value === 'true';
            else input.value = value;
            input.dispatchEvent(new Event('change', { bubbles: true }));
        }
    }

    getCSRFToken() {
        return document.querySelector('[name=csrfmiddlewaretoken]')?.value || '';
    }

    startTimer() {
        this.recordingStartTime = Date.now();
        this.timerInterval = setInterval(() => {
            this.recordingDuration = Math.floor((Date.now() - this.recordingStartTime) / 1000);
            const min = String(Math.floor(this.recordingDuration / 60)).padStart(2, '0');
            const sec = String(this.recordingDuration % 60).padStart(2, '0');

            if (this.recordButton) {
            this.recordButton.textContent = `Recording... ${min}:${sec}`;
            }
        }, 1000);
    }
    stopTimer() { clearInterval(this.timerInterval); }

    clearRecording() {
        this.audioBlob = null;
        this.audioChunks = [];
        this.recordingDuration = 0;
        this.updateRecordingUI();
        this.updateStatus('Ready to record.', 'info');
    }

    updateRecordingUI() {
        this.recordButton.disabled = this.isRecording;
        this.stopButton.disabled = !this.isRecording;
        this.playButton.disabled = !this.audioBlob;
        this.uploadButton.disabled = !this.audioBlob;
    }

    updateStatus(msg, type = 'info') {
        if (!this.statusElement) return;
        const icons = {
            'recording': 'fas fa-microphone',
            'loading': 'fas fa-spinner',
            'success': 'fas fa-check-circle',
            'error': 'fas fa-exclamation-circle',
            'info': 'fas fa-info-circle'
        };
        this.statusElement.innerHTML = `<i class="fas ${icons[type] || icons['info']}"></i> <span>${msg}</span>`;
        this.statusElement.className = `alert alert-${type}`;
    }
}

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    const formType = document.body.getAttribute('data-form-type');
    if (formType) window.voiceRecorder = new VoiceRecorder({ formType });
});