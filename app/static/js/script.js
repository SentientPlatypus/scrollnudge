document.addEventListener('DOMContentLoaded', () => {
    const requests = document.querySelectorAll('.request');
    const viewed = new Set();
    const selected = new Set();
    const viewTimes = {}; // Object to store view and selection times for each position
    const startTime = performance.now(); // Record the start time
    const penaltyPopup = document.getElementById('penalty-popup');
    const countdownElement = document.getElementById('countdown');
    const threshold = 72;

    // Function to check which rectangles are visible
    const checkVisibleRequests = () => {
        requests.forEach(request => {
            const rect = request.getBoundingClientRect();
            if (rect.top >= 0 && rect.bottom <= window.innerHeight) {
                const position = request.dataset.position;
                if (!viewed.has(position)) {
                    viewed.add(position);
                    const elapsedTime = (performance.now() - startTime) / 1000; // Time in seconds
                    if (!viewTimes[position]) {
                        viewTimes[position] = {};
                    }
                    viewTimes[position].viewedAt = elapsedTime;
                    console.log(`Position ${position} viewed at ${elapsedTime.toFixed(2)} seconds`);
                }
            }
        });
    };

    // Check visible rectangles on page load
    checkVisibleRequests();

    // Check visible rectangles when the user scrolls
    document.querySelector('.content').addEventListener('scroll', () => {
        checkVisibleRequests();
    });

    document.querySelectorAll('.select-button').forEach(button => {
        button.addEventListener('click', (event) => {
            const request = event.target.closest('.request');
            const featureA = parseFloat(request.dataset.featurea);
            const featureB = parseFloat(request.dataset.featureb);
            const featureC = parseFloat(request.dataset.featurec);
            const featureD = parseFloat(request.dataset.featured);
            const featureE = parseFloat(request.dataset.featuree);
            const featureF = parseFloat(request.dataset.featuref);
            const totalValue = featureA + featureB + featureC + featureD + featureE + featureF;

            console.log(featureA, featureB, featureC, featureD, featureE, featureF, "total val:", totalValue);

            const position = request.dataset.position;
            selected.add(position);

            if (!viewTimes[position]) {
                viewTimes[position] = {};
            }
            const selectionTime = (performance.now() - startTime) / 1000; // Time in seconds
            viewTimes[position].selectedAt = selectionTime;
            viewTimes[position].correct = totalValue >= threshold; // Log if the selection is correct
            console.log(`Position ${position} selected at ${selectionTime.toFixed(2)} seconds`);

            button.disabled = true;
            button.classList.add('selected');

            if (totalValue >= threshold) {
                button.style.backgroundColor = '#a0998c'; // Correct
            } else {
                button.style.backgroundColor = '#a0998c'; // Show penalty if incorrect
                showPenaltyPopup();
            }
        });
    });

    window.scrollBy(0, 1);
    window.scrollBy(0, -1);

    document.getElementById('refresh-button').addEventListener('click', () => {
        console.log('User ID:', userId);
        console.log('IP:', ip);
        console.log('Treatment:', treatment);
        console.log('Viewed:', Array.from(viewed));
        console.log('Selected:', Array.from(selected));
        console.log('View Times:', viewTimes);
        console.log('Run Number:', runNumber);

        // Send the viewed, selected, and view times data to the server here if needed
        fetch('/log_experiment_data', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                user_id: userId,
                email_id: emailId,
                ip: ip,
                treatment: treatment,
                viewed: Array.from(viewed),
                selected: Array.from(selected),
                view_times: viewTimes,
                run_number: runNumber
            })
        }).then(response => {
            if (response.ok) {
                console.log('Data sent successfully');
                window.location.href = '/run_experiment';
            } else {
                console.error('Error sending data');
            }
        }).catch(error => {
            console.error('Error:', error);
        });
    });

    function showPenaltyPopup() {
        penaltyPopup.style.display = 'flex';
        let timeLeft = 10;
        const countdownInterval = setInterval(() => {
            if (timeLeft <= 0) {
                clearInterval(countdownInterval);
                penaltyPopup.style.display = 'none';
            } else {
                countdownElement.textContent = timeLeft;
                timeLeft--;
            }
        }, 1000);
    }
});
