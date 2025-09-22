// Spiritual Functionality

// Load spiritual content on section activation
async function loadSpiritualContent() {
    await getNewQuote();
    await loadPractices();
    await loadAffirmations();
}

// Get new spiritual quote
async function getNewQuote(tradition = 'universal') {
    // Fallback quotes for when API is unavailable
    const fallbackQuotes = [
        { quote: "The best way to find yourself is to lose yourself in the service of others.", source: "Mahatma Gandhi", reflection: "Service to others brings meaning and purpose to our lives." },
        { quote: "Peace comes from within. Do not seek it without.", source: "Buddha", reflection: "True peace is found through inner work, not external circumstances." },
        { quote: "Yesterday I was clever, so I wanted to change the world. Today I am wise, so I am changing myself.", source: "Rumi", reflection: "Personal transformation is the key to creating positive change." },
        { quote: "The mind is everything. What you think you become.", source: "Buddha", reflection: "Our thoughts shape our reality and our experiences." },
        { quote: "In the middle of difficulty lies opportunity.", source: "Albert Einstein", reflection: "Challenges often contain the seeds of growth and transformation." }
    ];
    
    try {
        const quote = await SpiritualAPI.getQuote(tradition);
        
        const quoteElement = document.getElementById('dailyQuote');
        if (quoteElement) {
            quoteElement.innerHTML = `
                <p>"${quote.quote}"</p>
                ${quote.source ? `<cite>- ${quote.source}</cite>` : ''}
                ${quote.reflection ? `<p class="text-muted mt-md">${quote.reflection}</p>` : ''}
            `;
        }
    } catch (error) {
        console.error('Failed to load quote from API, using fallback:', error);
        
        // Use fallback quote
        const randomQuote = fallbackQuotes[Math.floor(Math.random() * fallbackQuotes.length)];
        const quoteElement = document.getElementById('dailyQuote');
        
        if (quoteElement) {
            quoteElement.innerHTML = `
                <p>"${randomQuote.quote}"</p>
                <cite>- ${randomQuote.source}</cite>
                <p class="text-muted mt-md">${randomQuote.reflection}</p>
            `;
        }
    }
}

// Load spiritual practices
async function loadPractices(goal = 'peace') {
    try {
        const data = await SpiritualAPI.getPractices(goal);
        
        const practicesList = document.getElementById('practicesList');
        if (practicesList && data.practices) {
            practicesList.innerHTML = data.practices.map(practice => `
                <div class="practice-item">
                    <h4>${practice.name}</h4>
                    <p>${practice.description}</p>
                    <div class="text-muted">
                        <small>Duration: ${practice.duration} | Tradition: ${practice.tradition}</small>
                    </div>
                </div>
            `).join('');
        }
    } catch (error) {
        console.error('Failed to load practices:', error);
    }
}

// Load affirmations
async function loadAffirmations(focus = 'general') {
    try {
        const data = await SpiritualAPI.getAffirmations(5, focus);
        
        const affirmationsList = document.getElementById('affirmationsList');
        if (affirmationsList && data.affirmations) {
            affirmationsList.innerHTML = data.affirmations.map(affirmation => `
                <div class="affirmation">
                    ${affirmation}
                </div>
            `).join('');
        }
    } catch (error) {
        console.error('Failed to load affirmations:', error);
    }
}

// Request spiritual guidance
async function requestGuidance() {
    const concern = prompt('What spiritual guidance do you seek?');
    if (!concern) return;
    
    try {
        showLoadingScreen();
        const guidance = await SpiritualAPI.getGuidance(concern);
        
        // Show guidance in modal
        const modal = document.createElement('div');
        modal.className = 'modal active';
        modal.innerHTML = `
            <div class="modal-content">
                <h2>Spiritual Guidance</h2>
                <div class="guidance-content">
                    <p>${guidance.guidance}</p>
                    <h3 class="mt-lg">Recommended Practices:</h3>
                    <ul>
                        ${guidance.practices.map(p => `<li>${p}</li>`).join('')}
                    </ul>
                </div>
                <button class="btn btn-primary" onclick="closeModal(this)">Thank You</button>
            </div>
        `;
        
        document.body.appendChild(modal);
        
    } catch (error) {
        console.error('Failed to get guidance:', error);
        showToast('Failed to get spiritual guidance', 'error');
    } finally {
        hideLoadingScreen();
    }
}