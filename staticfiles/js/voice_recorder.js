(function() {
    console.log('Voice recorder script loaded');

    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (!SpeechRecognition) {
        console.warn('Web Speech API not supported');
        document.querySelectorAll('.voice-field-btn, .voice-btn').forEach(btn => btn.style.display = 'none');
        return;
    }

    let activeRecognition = null;
    let activeButton = null;

    function showMessage(msg, type) {
        let statusDiv = document.getElementById('voice-status');
        if (statusDiv) {
            const span = statusDiv.querySelector('span');
            if (span) span.textContent = msg;
            statusDiv.className = `voice-status-message alert-${type}`;
            statusDiv.style.display = 'flex';
            setTimeout(() => statusDiv.style.display = 'none', 3000);
        } else {
            const toast = document.createElement('div');
            toast.textContent = msg;
            Object.assign(toast.style, {
                position: 'fixed', bottom: '20px', right: '20px', zIndex: '9999',
                padding: '10px 16px', borderRadius: '8px',
                backgroundColor: type === 'error' ? '#f44336' : (type === 'success' ? '#4caf50' : '#FFD700'),
                color: type === 'error' || type === 'success' ? 'white' : '#28282B',
                fontWeight: 'bold', boxShadow: '0 2px 10px rgba(0,0,0,0.2)',
                backdropFilter: 'blur(8px)'
            });
            document.body.appendChild(toast);
            setTimeout(() => toast.remove(), 3000);
        }
    }

    function toTitleCase(str) {
        if (!str) return str;
        const smallWords = /^(a|an|and|as|at|but|by|en|for|if|in|of|on|or|the|to|vs?\.?|via)$/i;
        return str.toLowerCase().split(' ').map((word, index) => {
            if (index !== 0 && smallWords.test(word)) {
                return word;
            }
            return word.charAt(0).toUpperCase() + word.slice(1);
        }).join(' ');
    }

    function parseNaturalDate(text) {
        if (/^\d{4}-\d{2}-\d{2}$/.test(text)) return text;
        const date = new Date(text);
        if (!isNaN(date.getTime())) {
            return `${date.getFullYear()}-${String(date.getMonth()+1).padStart(2,'0')}-${String(date.getDate()).padStart(2,'0')}`;
        }
        const patterns = [
            /(\w+)\s+(\d{1,2})(?:st|nd|rd|th)?\s+(\d{4})/i,
            /(\d{1,2})(?:st|nd|rd|th)?\s+(\w+)\s+(\d{4})/i
        ];
        const monthMap = {jan:'01',feb:'02',mar:'03',apr:'04',may:'05',jun:'06',jul:'07',aug:'08',sep:'09',oct:'10',nov:'11',dec:'12'};
        for (let p of patterns) {
            let m = text.match(p);
            if (m) {
                let monthStr, day, year;
                if (p === patterns[0]) { monthStr = m[1]; day = m[2]; year = m[3]; }
                else { day = m[1]; monthStr = m[2]; year = m[3]; }
                let month = monthMap[monthStr.toLowerCase().slice(0,3)];
                if (month && day && year) return `${year}-${month}-${String(day).padStart(2,'0')}`;
            }
        }
        return null;
    }

    const selectMappings = {
        employment_type: {
            'full time': 'FULL_TIME', 'fulltime': 'FULL_TIME', 'full-time': 'FULL_TIME',
            'part time': 'PART_TIME', 'parttime': 'PART_TIME', 'part-time': 'PART_TIME',
            'contract': 'CONTRACT', 'contractor': 'CONTRACT',
            'freelance': 'FREELANCE', 'freelancer': 'FREELANCE',
            'internship': 'INTERNSHIP', 'intern': 'INTERNSHIP',
            'temporary': 'TEMPORARY', 'temp': 'TEMPORARY'
        },
        status: {
            'ongoing': 'ONGOING', 'in progress': 'ONGOING',
            'completed': 'COMPLETED', 'finished': 'COMPLETED',
            'dropped': 'DROPPED', 'withdrawn': 'DROPPED'
        }
    };

    function handleCommand(text) {
        const lower = text.toLowerCase();
        if (lower.includes('submit') || lower.includes('save') || lower.includes('send')) {
            const form = document.querySelector('form');
            if (form) {
                showMessage('Submitting form...', 'info');
                form.dispatchEvent(new Event('submit', { bubbles: true }));
            } else {
                showMessage('No form found to submit.', 'error');
            }
            return true;
        }
        if (lower.includes('cancel') || lower.includes('go back')) {
            const cancelBtn = document.querySelector('.btn-cancel');
            if (cancelBtn) cancelBtn.click();
            else showMessage('No cancel button found.', 'error');
            return true;
        }

        const changeMatch = text.match(/change\s+(\w+(?:\s+\w+)?)\s+to\s+(.+)/i);
        const setMatch = text.match(/set\s+(\w+(?:\s+\w+)?)\s+to\s+(.+)/i);
        const match = changeMatch || setMatch;
        if (match) {
            let fieldName = match[1].toLowerCase().replace(/\s+/g, '_');
            let newValue = match[2].trim();
            newValue = toTitleCase(newValue); 

            const fieldMapping = {
                'company_name': 'company_name', 'company': 'company_name', 'company name': 'company_name',
                'job_title': 'job_title', 'job title': 'job_title', 'title': 'job_title',
                'salary_range': 'salary_range', 'salary': 'salary_range', 'salary range': 'salary_range',
                'school_name': 'school_name', 'school': 'school_name',
                'program': 'program', 'degree': 'program',
                'start_year': 'start_year', 'start year': 'start_year',
                'end_year': 'end_year', 'end year': 'end_year'
            };
            const targetId = fieldMapping[fieldName] || fieldName;
            const targetField = document.getElementById(targetId);
            if (targetField) {
                targetField.value = newValue;
                targetField.dispatchEvent(new Event('change', { bubbles: true }));
                showMessage(`Updated ${targetId} to "${newValue}"`, 'success');
                const transcriptField = document.getElementById('voice_transcript');
                if (transcriptField) transcriptField.value += (transcriptField.value ? ' | ' : '') + text;
                const voiceFlag = document.getElementById('created_via_voice');
                if (voiceFlag) voiceFlag.value = 'true';
            } else {
                showMessage(`Field "${fieldName}" not found.`, 'error');
            }
            return true;
        }
        return false;
    }

    function startListening(element, button, isGlobalCommand = false) {
        if (activeRecognition) activeRecognition.stop();

        const recognition = new SpeechRecognition();
        recognition.lang = 'en-US';
        recognition.interimResults = false;
        recognition.maxAlternatives = 1;

        recognition.onstart = () => {
            activeRecognition = recognition;
            activeButton = button;
            button.classList.add('listening');
            button.innerHTML = '<i class="fas fa-stop"></i>';
        };

        recognition.onresult = (event) => {
            const spokenText = event.results[0][0].transcript.trim();
            console.log('Heard:', spokenText);

            if (handleCommand(spokenText)) {
                recognition.stop();
                return;
            }

            if (element) {
                if (element.tagName === 'SELECT') {
                    const mapping = selectMappings[element.id];
                    if (mapping) {
                        const lowerText = spokenText.toLowerCase();
                        let matched = null;
                        for (let [phrase, val] of Object.entries(mapping)) {
                            if (lowerText.includes(phrase)) { matched = val; break; }
                        }
                        if (matched) {
                            element.value = matched;
                            element.dispatchEvent(new Event('change', { bubbles: true }));
                            showMessage(`Selected: ${element.options[element.selectedIndex]?.text}`, 'success');
                        } else {
                            showMessage(`Could not recognize "${spokenText}" for this dropdown.`, 'error');
                        }
                    }
                } else if (element.type === 'date') {
                    const parsed = parseNaturalDate(spokenText);
                    if (parsed) {
                        element.value = parsed;
                        element.dispatchEvent(new Event('change', { bubbles: true }));
                        showMessage(`Date set to ${parsed}`, 'success');
                    } else {
                        showMessage(`Could not parse "${spokenText}" as a date.`, 'error');
                    }
                } else {
                    const titleCased = toTitleCase(spokenText);
                    element.value = titleCased;
                    element.dispatchEvent(new Event('change', { bubbles: true }));
                    showMessage(`Filled: "${titleCased}"`, 'success');
                }

                const transcriptField = document.getElementById('voice_transcript');
                if (transcriptField) {
                    let existing = transcriptField.value;
                    transcriptField.value = existing ? existing + ' | ' + spokenText : spokenText;
                }
                const voiceFlag = document.getElementById('created_via_voice');
                if (voiceFlag) voiceFlag.value = 'true';
            } else {
                showMessage(`Heard: "${spokenText}"`, 'info');
            }
        };

        recognition.onerror = (event) => {
            console.error('Speech error:', event.error);
            let msg = 'Voice error: ';
            if (event.error === 'not-allowed') msg += 'Microphone permission denied.';
            else if (event.error === 'no-speech') msg += 'No speech detected.';
            else msg += event.error;
            showMessage(msg, 'error');
        };

        recognition.onend = () => {
            if (activeButton) {
                activeButton.classList.remove('listening');
                activeButton.innerHTML = '<i class="fas fa-microphone"></i>';
            }
            activeRecognition = null;
            activeButton = null;
        };

        recognition.start();
    }

    document.addEventListener('DOMContentLoaded', () => {
        const buttons = document.querySelectorAll('.voice-field-btn, .voice-btn');
        buttons.forEach(btn => {
            btn.addEventListener('click', (e) => {
                e.preventDefault();
                const targetId = btn.getAttribute('data-target');
                if (!targetId) {
                    startListening(null, btn, true);
                    return;
                }
                const targetField = document.getElementById(targetId);
                if (!targetField) {
                    showMessage(`Field "${targetId}" not found.`, 'error');
                    return;
                }
                if (activeRecognition && activeButton === btn) {
                    activeRecognition.stop();
                } else {
                    startListening(targetField, btn, false);
                }
            });
        });
    });
})();