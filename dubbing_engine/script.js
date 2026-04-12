const dropZone = document.getElementById('dropZone');
const fileInput = document.getElementById('fileInput');
const fileNameDisplay = document.getElementById('fileName');
const processBtn = document.getElementById('processBtn');
const languageSelect = document.getElementById('languageSelect');
const progressContainer = document.getElementById('progressContainer');
const progressFill = document.getElementById('progressFill');
const statusText = document.getElementById('statusText');
const resultSection = document.getElementById('resultSection');
const audioResult = document.getElementById('audioResult');
const downloadAudio = document.getElementById('downloadAudio');
const segmentsBody = document.querySelector('#segmentsTable tbody');

let selectedFile = null;

// Drag and drop handling
dropZone.addEventListener('click', () => fileInput.click());

dropZone.addEventListener('dragover', (e) => {
    e.preventDefault();
    dropZone.classList.add('active');
});

dropZone.addEventListener('dragleave', () => dropZone.classList.remove('active'));

dropZone.addEventListener('drop', (e) => {
    e.preventDefault();
    dropZone.classList.remove('active');
    handleFiles(e.dataTransfer.files);
});

fileInput.addEventListener('change', (e) => handleFiles(e.target.files));

function handleFiles(files) {
    if (files.length > 0) {
        selectedFile = files[0];
        fileNameDisplay.textContent = `Selected: ${selectedFile.name} (${(selectedFile.size / 1024 / 1024).toFixed(1)}MB)`;
    }
}

// Processing logic
processBtn.addEventListener('click', async () => {
    if (!selectedFile) {
        alert("Please select an audio file first.");
        return;
    }

    const language = languageSelect.value;
    const formData = new FormData();
    formData.append('file', selectedFile);
    formData.append('target_lang', language);

    // Update UI for processing
    processBtn.disabled = true;
    progressContainer.classList.remove('hidden');
    resultSection.classList.add('hidden');
    progressFill.style.width = '20%';
    statusText.textContent = "Uploading and transcribing...";

    try {
        const response = await fetch(`/translate`, {
            method: 'POST',
            body: formData
        });

        if (!response.ok) {
            const errorText = await response.text();
            throw new Error(`Server error (${response.status}): ${errorText || response.statusText}`);
        }

        const data = await response.json();

        if (data.status === 'success') {
            progressFill.style.width = '100%';
            statusText.textContent = "Translation Complete!";
            showResults(data);
        } else {
            throw new Error(data.message || "Processing failed");
        }
    } catch (error) {
        console.error(error);
        alert(`Error: ${error.message}`);
        statusText.textContent = "Error occurred during processing.";
    } finally {
        processBtn.disabled = false;
    }
});

function showResults(data) {
    resultSection.classList.remove('hidden');
    
    // Set audio and download
    if (audioResult) {
        audioResult.src = data.audio_url;
    }
    if (downloadAudio) {
        downloadAudio.href = data.audio_url;
        downloadAudio.download = data.metadata ? data.metadata.output_file : "dubbed_audio.mp3";
    }
    
    // Display processing metadata if available
    if (data.metadata) {
        const metadata = data.metadata;
        console.log("Processing Complete:", metadata);
        if (statusText) {
            statusText.innerHTML += `<br>Processed ${metadata.successful_segments}/${metadata.total_segments} segments in ${metadata.processing_time_seconds.toFixed(1)}s`;
        }
    }
    
    // Fill segments table
    if (segmentsBody) {
        segmentsBody.innerHTML = '';
        (data.segments || []).forEach((seg, idx) => {
            const row = document.createElement('tr');
            row.innerHTML = `
                <td>${seg.start ? seg.start.toFixed(1) : '?'}s - ${seg.end ? seg.end.toFixed(1) : '?'}s</td>
                <td><span class="badge ${seg.emotion || 'neutral'}">${seg.emotion || 'neutral'}</span></td>
                <td>${seg.gender || 'unknown'}</td>
                <td>${seg.age_group || 'unknown'}</td>
                <td><span class="voice-tag ${seg.voice_profile || 'default'}">${seg.voice_profile || 'Default'}</span></td>
                <td class="translation-cell">${seg.translated_text || ''}</td>
            `;
            segmentsBody.appendChild(row);
        });
    }

    // Smooth scroll to results
    resultSection.scrollIntoView({ behavior: 'smooth' });
    
    // Load lyrics editor if job_id is available
    if (data.job_id) {
        loadLyricsEditor(data.job_id, data.segments || []);
    }
}

// LYRICS EDITOR FUNCTIONS
let currentJobId = null;

function loadLyricsEditor(jobId, segments) {
    currentJobId = jobId;
    const editorTab = document.getElementById('editor-tab');
    const overviewTab = document.getElementById('overview-tab');
    
    if (!editorTab || !overviewTab) return;
    
    // Clear existing content
    editorTab.innerHTML = '';
    overviewTab.innerHTML = '';
    
    // Populate Overview tab with table
    const table = document.createElement('table');
    table.className = 'segments-table';
    table.innerHTML = `
        <thead>
            <tr>
                <th>Time</th>
                <th>Emotion</th>
                <th>Gender</th>
                <th>Age</th>
                <th>Voice</th>
                <th>Preview</th>
            </tr>
        </thead>
        <tbody></tbody>
    `;
    
    const tbody = table.querySelector('tbody');
    segments.forEach((seg, idx) => {
        const row = document.createElement('tr');
        row.innerHTML = `
            <td>${seg.start?.toFixed(1) || '?'}s - ${seg.end?.toFixed(1) || '?'}s</td>
            <td><span class="badge ${seg.emotion || 'neutral'}">${seg.emotion || 'neutral'}</span></td>
            <td>${seg.gender || 'unknown'}</td>
            <td>${seg.age_group || 'unknown'}</td>
            <td><span class="voice-tag">${seg.voice_profile || 'Default'}</span></td>
            <td><span class="text-preview">${seg.translated_text?.substring(0, 20) || ''}...</span></td>
        `;
        tbody.appendChild(row);
    });
    overviewTab.appendChild(table);
    
    // Populate Editor tab with segment editors
    const segmentsList = document.createElement('div');
    segmentsList.className = 'segments-list';
    
    segments.forEach((seg, idx) => {
        const segmentDiv = createSegmentEditor(seg, idx, jobId);
        segmentsList.appendChild(segmentDiv);
    });
    
    const actionsDiv = document.createElement('div');
    actionsDiv.className = 'editor-actions';
    actionsDiv.innerHTML = `
        <button class="rebuild-btn" onclick="rebuildAudio('${jobId}')">
            🔄 Rebuild Audio with All Changes
        </button>
    `;
    
    editorTab.appendChild(segmentsList);
    editorTab.appendChild(actionsDiv);
}

function createSegmentEditor(segment, index, jobId) {
    const div = document.createElement('div');
    div.className = 'segment-editor';
    div.id = `segment-${index}`;
    
    const voiceOpts = {
        'en-US': ['en-US-AIGenerate1Standard', 'en-US-AIGenerate1Neural'],
        'ta-IN': ['ta-IN-PallaviNeural', 'ta-IN-SaranyaNeural'],
        'te-IN': ['te-IN-MohanNeural', 'te-IN-ShrutiNeural'],
        'hi-IN': ['hi-IN-MadhurNeural', 'hi-IN-KalpanaNeural']
    };
    
    div.innerHTML = `
        <div class="segment-editor-header">
            <span class="segment-time">${segment.start?.toFixed(2) || '0.00'}s - ${segment.end?.toFixed(2) || '0.00'}s</span>
            <span class="segment-id">Segment #${index + 1}</span>
        </div>
        
        <div class="lyrics-pair">
            <div class="lyrics-field">
                <label class="lyrics-label">Original Text</label>
                <textarea class="lyrics-input" readonly>${segment.original_text || '(No original text)'}</textarea>
            </div>
            <div class="lyrics-field">
                <label class="lyrics-label">Translated Text (Editable)</label>
                <textarea class="lyrics-input" id="translated-${index}">${segment.translated_text || ''}</textarea>
            </div>
        </div>
        
        <div class="voice-controls">
            <div class="control-group">
                <label class="lyrics-label">Gender</label>
                <select class="voice-select" id="gender-${index}">
                    <option value="male" ${segment.gender === 'male' ? 'selected' : ''}>Male</option>
                    <option value="female" ${segment.gender === 'female' ? 'selected' : ''}>Female</option>
                </select>
            </div>
            <div class="control-group">
                <label class="lyrics-label">Age Group</label>
                <select class="voice-select" id="age-${index}">
                    <option value="child" ${segment.age_group === 'child' ? 'selected' : ''}>Child</option>
                    <option value="young_adult" ${segment.age_group === 'young_adult' ? 'selected' : ''}>Young Adult</option>
                    <option value="adult" ${segment.age_group === 'adult' ? 'selected' : ''}>Adult</option>
                    <option value="elderly" ${segment.age_group === 'elderly' ? 'selected' : ''}>Elderly</option>
                </select>
            </div>
            <div class="control-group">
                <label class="lyrics-label">Emotion</label>
                <select class="voice-select" id="emotion-${index}" disabled>
                    <option>${segment.emotion || 'neutral'}</option>
                </select>
            </div>
        </div>
        
        <div class="segment-buttons">
            <button class="seg-btn save-btn" onclick="saveSegment(${index}, '${jobId}')">
                💾 Save Text
            </button>
            <button class="seg-btn regen-btn" onclick="regenerateSegment(${index}, '${jobId}')">
                🎤 Regenerate Audio
            </button>
        </div>
        <div class="status-message" id="status-${index}"></div>
    `;
    
    return div;
}

async function saveSegment(segmentId, jobId) {
    const translatedInput = document.getElementById(`translated-${segmentId}`);
    if (!translatedInput) return;
    
    const newText = translatedInput.value;
    const statusDiv = document.getElementById(`status-${segmentId}`);
    
    try {
        const response = await fetch(`/edit-segment/${jobId}`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                segment_id: segmentId,
                new_translated_text: newText
            })
        });
        
        const data = await response.json();
        
        if (response.ok) {
            showStatus(statusDiv, 'Text saved successfully!', 'success');
        } else {
            showStatus(statusDiv, `Error: ${data.error || 'Failed to save'}`, 'error');
        }
    } catch (error) {
        console.error('Save failed:', error);
        showStatus(statusDiv, 'Error saving text', 'error');
    }
}

async function regenerateSegment(segmentId, jobId) {
    const genderSelect = document.getElementById(`gender-${segmentId}`);
    const ageSelect = document.getElementById(`age-${segmentId}`);
    const statusDiv = document.getElementById(`status-${segmentId}`);
    
    if (!genderSelect || !ageSelect) return;
    
    const gender = genderSelect.value;
    const ageGroup = ageSelect.value;
    
    try {
        showStatus(statusDiv, 'Regenerating audio...', 'info');
        
        const response = await fetch(`/regenerate-segment/${jobId}`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
            body: `segment_id=${segmentId}&gender=${gender}&age_group=${ageGroup}`
        });
        
        const data = await response.json();
        
        if (response.ok) {
            showStatus(statusDiv, 'Audio regenerated! Rebuild to apply changes.', 'success');
        } else {
            showStatus(statusDiv, `Error: ${data.error || 'Failed to regenerate'}`, 'error');
        }
    } catch (error) {
        console.error('Regenerate failed:', error);
        showStatus(statusDiv, 'Error regenerating audio', 'error');
    }
}

async function rebuildAudio(jobId) {
    try {
        const statusText = document.querySelector('.status-text') || statusText;
        if (statusText) statusText.textContent = 'Rebuilding audio with changes...';
        
        const response = await fetch(`/rebuild-audio/${jobId}`, {
            method: 'POST'
        });
        
        const data = await response.json();
        
        if (response.ok) {
            // Reload the audio player with new file
            if (audioResult) {
                audioResult.src = data.audio_url;
                audioResult.load();
            }
            alert('Audio rebuilt successfully!');
        } else {
            throw new Error(data.error || 'Failed to rebuild audio');
        }
    } catch (error) {
        console.error('Rebuild failed:', error);
        alert(`Error rebuilding audio: ${error.message}`);
    }
}

function switchTab(tabName) {
    // Hide all tabs
    document.querySelectorAll('.tab-content').forEach(tab => {
        tab.classList.remove('active');
    });
    
    // Deactivate all buttons
    document.querySelectorAll('.tab-btn').forEach(btn => {
        btn.classList.remove('active');
    });
    
    // Show selected tab
    const selectedTab = document.getElementById(`${tabName}-tab`);
    if (selectedTab) {
        selectedTab.classList.add('active');
    }
    
    // Activate selected button
    event.target.classList.add('active');
}

function showStatus(statusDiv, message, type) {
    if (!statusDiv) return;
    
    statusDiv.textContent = message;
    statusDiv.className = `status-message show ${type}`;
    
    if (type !== 'info') {
        setTimeout(() => {
            statusDiv.className = 'status-message';
        }, 5000);
    }
}
