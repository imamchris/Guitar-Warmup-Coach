function closeModal() {
    document.getElementById('feedbackModal').style.display = 'none';
}

// Show modal after clicking "Next" button on any exercise page
document.addEventListener('DOMContentLoaded', function() {
    var nextForm = document.getElementById('nextExerciseForm') ||
                   document.getElementById('nextScaleForm') ||
                   document.getElementById('nextDailyForm');
    var feedbackModal = document.getElementById('feedbackModal');
    if (nextForm && feedbackModal) {
        nextForm.addEventListener('submit', function(e) {
            e.preventDefault();
            feedbackModal.style.display = 'flex';
        });
    }
});