document.addEventListener('DOMContentLoaded', () => {
    const requests = document.querySelectorAll('.request');
    const viewed = new Set();
    const selected = new Set();
    const penaltyPopup = document.getElementById('penalty-popup');
    const countdownElement = document.getElementById('countdown');

    document.querySelector('.content').addEventListener('scroll', () => {
        requests.forEach(request => {
            const rect = request.getBoundingClientRect();
            if (rect.top >= 0 && rect.bottom <= window.innerHeight) {
                viewed.add(request.dataset.position);
            }
        });
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
            console.log(featureA, featureB, featureC, featureD, featureE, featureF, "total val:", totalValue)
            if (totalValue >= 50) {
                request.style.backgroundColor = 'green';
            } else {
                request.style.backgroundColor = 'red';
                showPenaltyPopup();
            }

            selected.add(request.dataset.position);
        });
    });

    document.getElementById('refresh-button').addEventListener('click', () => {
        console.log('User ID:', userId);
        console.log('Treatment:', treatment);
        console.log('Viewed:', Array.from(viewed));
        console.log('Selected:', Array.from(selected));
        console.log('Run Numebr:', runNumber);
        // Send the viewed and selected data to the server here if needed
        fetch('/log_experiment_data', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                user_id: userId,
                treatment: treatment,
                viewed: Array.from(viewed),
                selected: Array.from(selected),
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
