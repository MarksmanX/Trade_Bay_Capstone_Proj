
document.addEventListener('DOMContentLoaded', function () {
    // Event listener for offer item button
    document.querySelectorAll('.offer-item-btn').forEach(button => {
        button.addEventListener('click', function () {
            const itemId = this.dataset.itemId;
            
            // Send AJAX request to add-offered-item route
            fetch('/add-offered-item', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': '{{ csrf_token() }}'
                },
                body: JSON.stringify({ item_id: itemId })
            })
            .then(response => {
                if (!response.ok && response.status === 401) {
                    // If user is not logged in, flash a message or redirect them to login
                    alert('You must log in to offer items.');
                }
                return response.json();
            })
            .then(data => {
                if (data.success) {
                    alert('Item successfully added to offered items list');
                } else {
                    alert(data.error);
                }
            })
            .catch(error => console.error('Error:', error));
        });
    });

    // Event listener for request item button
    document.querySelectorAll('.request-item-btn').forEach(button => {
        button.addEventListener('click', function () {
            const itemId = this.dataset.itemId;

            // Send AJAX request to add-requested-item route
            fetch('/add-requested-item', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': '{{ csrf_token() }}'
                },
                body: JSON.stringify({ item_id: itemId })
            })
            .then(response => {
                if (!response.ok && response.status === 401) {
                    // If user is not logged in, flash a message or redirect them to login
                    alert('You must log in to offer items.');
                }
                return response.json();
            })
            .then(data => {
                if (data.success) {
                    alert('Item successfully added to requested items list');
                } else {
                    alert(data.error);
                }
            })
            .catch(error => console.error('Error:', error));
        });
    });
});

document.addEventListener('DOMContentLoaded', function () {
    // Event listener for remove item button
    document.querySelectorAll('.remove-item-btn').forEach(button => {
        button.addEventListener('click', function () {
            const itemId = this.dataset.itemId;
            const itemType = this.dataset.itemType;

            fetch('/remove-item', {
                method: 'DELETE',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': '{{ csrf_token() }}'
                },
                body: JSON.stringify({ item_id: itemId, item_type: itemType })
            })
            .then(response => {
                if (!response.ok && response.status === 401) {
                    // If user is not logged in, flash a message or redirect them to login
                    alert('You must log in to offer items.');
                }
                return response.json();
            })
            .then(data => {
                if (data.success) {
                    alert('Item successfully removed from list!');
                    // Optionally refresh the page or remove the item from the DOM
                    window.location.reload();  // Reload to see the updated list
                } else {
                    alert(data.error);
                }
            })
            .catch(error => console.error('Error:', error));
        });
    });
});

//Initiating a Trade
document.addEventListener('DOMContentLoaded', function () {
    const tradeButton = document.getElementById('initiate-trade-btn');

    if (tradeButton) {
        tradeButton.addEventListener('click', function () {
            // Get the selected item IDs
            const yourItemId = document.querySelector('input[name="your_item"]:checked')?.value;
            const theirItemId = document.querySelector('input[name="their_item"]:checked')?.value;

            if (!yourItemId || !theirItemId) {
                alert('Please select both items for the trade.');
                return;
            }
            
            console.log('Your Item ID:', yourItemId);
            console.log('Their Item ID:', theirItemId);
            
            // Send trade initiation request
            fetch('/initiate-trade', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': '{{ csrf_token() }}'
                },
                body: JSON.stringify({ your_item_id: yourItemId, their_item_id: theirItemId })
            })
            .then(response => {
                if (!response.ok && response.status === 401) {
                    // If user is not logged in, flash a message or redirect them to login
                    alert('You must log in to offer items.');
                }
                return response.json();
            })
            .then(data => {
                if (data.success) {
                    alert('Trade initiated successfully!');
                    document.getElementById('trade-feedback').innerText = 'Trade initiated successfully!';
                } else {
                    alert(data.error);
                }
            })
            .catch(error => console.error('Error:', error));
        });
    }
});

//Accepting and Rejecting Pending Trades
document.addEventListener('DOMContentLoaded', function () {
    document.querySelectorAll('.accept-trade-btn').forEach(button => {
        button.addEventListener('click', function () {
            const tradeId = this.dataset.tradeId;

            fetch(`/accept-trade/${tradeId}`, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': '{{ csrf_token() }}'
                }
            })
            .then(response => {
                if (!response.ok && response.status === 401) {
                    // If user is not logged in, flash a message or redirect them to login
                    alert('You must log in to offer items.');
                }
                return response.json();
            })
            .then(data => {
                if (data.success) {
                    alert('Trade accepted!');
                    window.location.reload();
                } else {
                    alert(data.error);
                }
            })
            .catch(error => console.error('Error:', error));
        });
    });

    document.querySelectorAll('.reject-trade-btn').forEach(button => {
        button.addEventListener('click', function () {
            const tradeId = this.dataset.tradeId;

            fetch(`/reject-trade/${tradeId}`, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': '{{ csrf_token() }}'
                }
            })
            .then(response => {
                if (!response.ok && response.status === 401) {
                    // If user is not logged in, flash a message or redirect them to login
                    alert('You must log in to offer items.');
                }
                return response.json();
            })
            .then(data => {
                if (data.success) {
                    alert('Trade rejected!');
                    window.location.reload();
                } else {
                    alert(data.error);
                }
            })
            .catch(error => console.error('Error:', error));
        });
    });
});

document.addEventListener('DOMContentLoaded', function () {
    const loadingIndicator = document.getElementById('loading-indicator');
    const resultsContainer = document.getElementById('results-container');
    
    document.getElementById('search-button').addEventListener('click', function () {
        const query = document.getElementById('search-input').value;

        // Show the loading indicator
        loadingIndicator.style.display = 'block';
        resultsContainer.innerHTML = ''; // Clear any previous results
        
        fetch(`/items/search?q=${encodeURIComponent(query)}`, {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json',
                'Accept': 'application/json',
                'X-CSRFToken': '{{ csrf_token() }}'
            }
        })
        .then(response => {
            if (!response.ok && response.status === 401) {
                // If user is not logged in, flash a message or redirect them to login
                alert('You must log in to offer items.');
            }
            return response.json();
        })
        .then(data => {
            // Hide the loading indicator
            loadingIndicator.style.display = 'none';

            if (data.success) {
                // Display the results
                let resultsHTML = '';
                data.items.forEach(item => {
                    resultsHTML += `<div>${item.title}</div>`;
                });
                resultsContainer.innerHTML = resultsHTML;
            } else {
                alert(data.error);
            }
        })
        .catch(error => {
            loadingIndicator.style.display = 'none';
            console.error('Fetch Error:', error);
            alert(`There was an error processing your request: ${error.message}`);
        });
    });
});