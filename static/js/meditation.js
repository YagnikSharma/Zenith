// Meditation Functionality

let meditationTimer = null;
let meditationStartTime = null;
let meditationDuration = 0;

// Load meditation stats
async function loadMeditationStats() {
    if (STATE.isGuest) return;
    
    try {
        const stats = await MeditationAPI.getStats();
        
        document.getElementById('totalSessions').textContent = stats.total_sessions || 0;
        document.getElementById('totalMinutes').textContent = stats.total_minutes || 0;
        document.getElementById('streakDays').textContent = stats.streak_days || 0;
        
    } catch (error) {
        console.error('Failed to load meditation stats:', error);
    }
}

// Start meditation timer
function startMeditation() {
    const duration = parseInt(document.getElementById('meditationDuration').value);
    meditationDuration = duration;
    meditationStartTime = Date.now();
    
    const timerDisplay = document.getElementById('timerDisplay');
    const button = event.target;
    
    // Change button to stop
    button.innerHTML = '<span class="material-icons">stop</span> Stop';
    button.onclick = stopMeditation;
    
    // Add progress ring if not exists
    const timerContainer = document.querySelector('.timer-display');
    if (!timerContainer.querySelector('.progress-ring')) {
        const progressRing = document.createElement('div');
        progressRing.className = 'progress-ring';
        progressRing.innerHTML = `
            <svg class="progress-ring__svg" width="200" height="200">
                <circle class="progress-ring__circle-bg" cx="100" cy="100" r="90" />
                <circle class="progress-ring__circle" cx="100" cy="100" r="90" />
            </svg>
        `;
        timerContainer.appendChild(progressRing);
    }
    
    // Setup progress ring
    const circle = document.querySelector('.progress-ring__circle');
    const radius = circle.r.baseVal.value;
    const circumference = radius * 2 * Math.PI;
    circle.style.strokeDasharray = `${circumference} ${circumference}`;
    circle.style.strokeDashoffset = circumference;
    
    // Start countdown
    let remainingTime = duration * 60;
    const totalTime = duration * 60;
    
    meditationTimer = setInterval(() => {
        const minutes = Math.floor(remainingTime / 60);
        const seconds = remainingTime % 60;
        timerDisplay.textContent = `${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`;
        
        // Update progress ring
        const progress = (totalTime - remainingTime) / totalTime;
        const offset = circumference - (progress * circumference);
        circle.style.strokeDashoffset = offset;
        
        // Add pulse effect in last 10 seconds
        if (remainingTime <= 10 && remainingTime > 0) {
            timerDisplay.classList.add('pulse');
        }
        
        remainingTime--;
        
        if (remainingTime < 0) {
            completeMeditation();
        }
    }, 1000);
    
    // Play start sound (if available)
    playMeditationSound('start');
    
    showToast('Meditation started. Focus on your breath...', 'info');
}

// Stop meditation
function stopMeditation() {
    if (meditationTimer) {
        clearInterval(meditationTimer);
        meditationTimer = null;
        
        const actualDuration = Math.floor((Date.now() - meditationStartTime) / 60000);
        
        // Log partial session if more than 1 minute
        if (actualDuration >= 1) {
            logMeditationSession(actualDuration, 'interrupted');
        }
        
        // Reset display
        document.getElementById('timerDisplay').textContent = '00:00';
        
        // Reset button
        const button = event.target.closest('button');
        button.innerHTML = '<span class="material-icons">play_arrow</span> Start';
        button.onclick = startMeditation;
        
        showToast('Meditation stopped', 'info');
    }
}

// Complete meditation
function completeMeditation() {
    clearInterval(meditationTimer);
    meditationTimer = null;
    
    // Play completion sound
    playMeditationSound('complete');
    
    // Show mood tracking modal
    if (!STATE.isGuest) {
        showMoodModal(meditationDuration);
    }
    
    // Reset display
    document.getElementById('timerDisplay').textContent = '00:00';
    
    // Reset button
    const buttons = document.querySelectorAll('.timer-controls button');
    buttons.forEach(btn => {
        if (btn.textContent.includes('Stop')) {
            btn.innerHTML = '<span class="material-icons">play_arrow</span> Start';
            btn.onclick = startMeditation;
        }
    });
    
    showToast('Meditation completed! Well done! 🎉', 'success');
}

// Show mood tracking modal
function showMoodModal(duration) {
    const modal = document.createElement('div');
    modal.className = 'modal active';
    modal.innerHTML = `
        <div class="modal-content">
            <h2>How was your meditation?</h2>
            <div class="mood-tracking">
                <label>Mood before (1-10):</label>
                <input type="range" id="moodBefore" min="1" max="10" value="5">
                <span id="moodBeforeValue">5</span>
                
                <label>Mood after (1-10):</label>
                <input type="range" id="moodAfter" min="1" max="10" value="7">
                <span id="moodAfterValue">7</span>
                
                <label>Notes (optional):</label>
                <textarea id="meditationNotes" rows="3" placeholder="How do you feel?"></textarea>
            </div>
            <div style="display: flex; gap: 16px; justify-content: flex-end;">
                <button class="btn btn-secondary" onclick="closeModal(this)">Skip</button>
                <button class="btn btn-primary" onclick="saveMeditationSession(${duration}, this)">Save</button>
            </div>
        </div>
    `;
    
    document.body.appendChild(modal);
    
    // Add range listeners
    document.getElementById('moodBefore').addEventListener('input', (e) => {
        document.getElementById('moodBeforeValue').textContent = e.target.value;
    });
    document.getElementById('moodAfter').addEventListener('input', (e) => {
        document.getElementById('moodAfterValue').textContent = e.target.value;
    });
}

// Save meditation session
async function saveMeditationSession(duration, button) {
    const moodBefore = parseInt(document.getElementById('moodBefore').value);
    const moodAfter = parseInt(document.getElementById('moodAfter').value);
    const notes = document.getElementById('meditationNotes').value;
    
    await logMeditationSession(duration, 'completed', moodBefore, moodAfter, notes);
    
    closeModal(button);
    loadMeditationStats();
}

// Log meditation session
async function logMeditationSession(duration, type, moodBefore = null, moodAfter = null, notes = null) {
    if (STATE.isGuest) return;
    
    try {
        const result = await MeditationAPI.logSession(duration, type, moodBefore, moodAfter, notes);
        
        if (result.stats) {
            document.getElementById('totalSessions').textContent = result.stats.total_sessions;
            document.getElementById('totalMinutes').textContent = result.stats.total_minutes;
            document.getElementById('streakDays').textContent = result.stats.streak_days;
            
            if (result.stats.mood_improvement !== null && result.stats.mood_improvement > 0) {
                showToast(`Mood improved by ${result.stats.mood_improvement} points! 🌟`, 'success');
            }
        }
        
    } catch (error) {
        console.error('Failed to log meditation session:', error);
    }
}

// Start breathing exercise
async function startBreathing(type) {
    try {
        const exercise = await MeditationAPI.getBreathingExercise(type);
        
        // Show breathing guide modal
        const modal = document.createElement('div');
        modal.className = 'modal active';
        modal.innerHTML = `
            <div class="modal-content">
                <h2>${exercise.exercise.name}</h2>
                <p>${exercise.exercise.description}</p>
                
                <div class="breathing-guide">
                    <h3>Instructions:</h3>
                    <ol>
                        ${exercise.exercise.instructions.map(i => `<li>${i}</li>`).join('')}
                    </ol>
                </div>
                
                <div class="breathing-animation" id="breathingAnimation">
                    <div class="breath-circle"></div>
                    <div class="breath-text">Get Ready...</div>
                </div>
                
                <div class="mt-lg">
                    <strong>Duration:</strong> ${exercise.exercise.duration}
                </div>
                
                <div style="display: flex; gap: 16px; justify-content: center; margin-top: 24px;">
                    <button class="btn btn-primary" onclick="startBreathingAnimation('${type}')">Start Exercise</button>
                    <button class="btn btn-secondary" onclick="closeModal(this)">Close</button>
                </div>
            </div>
        `;
        
        document.body.appendChild(modal);
        
    } catch (error) {
        console.error('Failed to load breathing exercise:', error);
        showToast('Failed to load breathing exercise', 'error');
    }
}

// Start breathing animation
function startBreathingAnimation(type) {
    const circle = document.querySelector('.breath-circle');
    const text = document.querySelector('.breath-text');
    
    if (!circle || !text) return;
    
    // Define breathing patterns
    const patterns = {
        '4-7-8': [
            { action: 'Inhale', duration: 4000 },
            { action: 'Hold', duration: 7000 },
            { action: 'Exhale', duration: 8000 }
        ],
        'box': [
            { action: 'Inhale', duration: 4000 },
            { action: 'Hold', duration: 4000 },
            { action: 'Exhale', duration: 4000 },
            { action: 'Hold', duration: 4000 }
        ],
        'belly': [
            { action: 'Inhale', duration: 4000 },
            { action: 'Exhale', duration: 4000 }
        ]
    };
    
    const pattern = patterns[type] || patterns['4-7-8'];
    let step = 0;
    
    function animate() {
        const current = pattern[step % pattern.length];
        text.textContent = current.action;
        
        if (current.action === 'Inhale') {
            circle.style.transform = 'scale(1.5)';
            circle.style.background = 'var(--primary-orange)';
        } else if (current.action === 'Exhale') {
            circle.style.transform = 'scale(0.8)';
            circle.style.background = 'var(--charcoal-medium)';
        } else {
            circle.style.transform = 'scale(1.2)';
            circle.style.background = 'var(--primary-orange-light)';
        }
        
        step++;
        
        if (step < pattern.length * 3) { // 3 cycles
            setTimeout(animate, current.duration);
        } else {
            text.textContent = 'Complete!';
            showToast('Breathing exercise completed!', 'success');
        }
    }
    
    animate();
}

// Play meditation sound
function playMeditationSound(type) {
    // Placeholder for sound implementation
    // In production, would play actual audio files
    console.log(`Playing ${type} sound`);
}

// Play grounding exercise
function playGroundingExercise() {
    const modal = document.createElement('div');
    modal.className = 'modal active';
    modal.innerHTML = `
        <div class="modal-content">
            <h2>5-4-3-2-1 Grounding Exercise</h2>
            <p>This exercise helps you reconnect with the present moment.</p>
            
            <div class="grounding-steps">
                <div class="step">
                    <strong>5 Things You Can See:</strong>
                    <p>Look around and name 5 things you can see right now.</p>
                </div>
                <div class="step">
                    <strong>4 Things You Can Touch:</strong>
                    <p>Notice 4 things you can physically touch and feel their texture.</p>
                </div>
                <div class="step">
                    <strong>3 Things You Can Hear:</strong>
                    <p>Listen and identify 3 sounds in your environment.</p>
                </div>
                <div class="step">
                    <strong>2 Things You Can Smell:</strong>
                    <p>Notice 2 scents around you (or remember favorite smells).</p>
                </div>
                <div class="step">
                    <strong>1 Thing You Can Taste:</strong>
                    <p>Focus on 1 taste in your mouth or sip some water.</p>
                </div>
            </div>
            
            <button class="btn btn-primary" onclick="closeModal(this)">I Feel Grounded</button>
        </div>
    `;
    
    document.body.appendChild(modal);
}