// static/app.js

document.addEventListener('DOMContentLoaded', function() {

    // Update the footer with the current year
    document.getElementById('year').textContent = new Date().getFullYear();

    // Fetch and display the latest data on page load
    fetchLatestData();
    // Fetch the initial count when the page loads
    fetchUsageCount();

    // Periodically update the count (e.g., every minute)
    setInterval(fetchUsageCount, 60000); // 60000 milliseconds = 1 minute

    // Handle the tea recommendation form submission
    document.getElementById('tea-form').addEventListener('submit', function(event) {
        event.preventDefault();

        var symptoms = document.getElementById('symptoms').value;
     
        fetch('/submit', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ symptoms: symptoms }),
        })
        .then(response => response.json())
        .then(data => {
            // Update with the server's response once it's received
            document.getElementById('result-summary').textContent = data.description;
            fetchLatestData(); // Refresh the latest data
            fetchUsageCount();
        })
        .catch((error) => {
            console.error('Error:', error);
            document.getElementById('result').textContent = `Error: ${error.message}`;
        });
    });
    
    // Add the new function to fetch and display the latest data
    function fetchLatestData() {
        /*let cachedData = localStorage.getItem('latestData');
        if (cachedData) {
            displayLatestData(JSON.parse(cachedData));
        } else {
            fetch('/get-latest-data')
                .then(response => response.json())
                .then(data => {
                    localStorage.setItem('latestData', JSON.stringify(data));
                    displayLatestData(data);
                })
                .catch(error => console.error('Error:', error));
        }*/

        fetch('/get-latest-data')
        .then(response => response.json())
        .then(data => {
            localStorage.setItem('latestData', JSON.stringify(data));
            displayLatestData(data);
        })
        .catch(error => console.error('Error:', error));
    }

    function updateResultSummary(message) {
        const resultSummary = document.getElementById('result-summary');
        if (resultSummary) {
            resultSummary.textContent = message;
        }
    }

    function displayLatestData(data) {
        let resultList = document.getElementById('result-list');
        resultList.innerHTML = ''; // Clear existing list
        data.forEach(entry => {
            let listItem = document.createElement('li');

            listItem.setAttribute('data-entry-id', entry.id);
        
            // Include the timestamp, description, and recommendation in the text content
            let contentSpan = document.createElement('span');
            contentSpan.className = 'entry-content';
            //contentSpan.textContent = `[${entry.timestamp}] ${entry.description} | ${entry.recommendation}`;
            contentSpan.innerHTML = `<span class="timestamp">${entry.timestamp}</span><br>------<br><strong>User:</strong> ${entry.description}<br>------<br><strong>TCM:</strong> ${entry.recommendation}`;
    
            // Create a container for buttons
            let buttonContainer = document.createElement('div');
            buttonContainer.className = 'button-container';
    
            // Create buttons for each action
            let thumbUpButton = document.createElement('button');
            thumbUpButton.className = 'thumb-up';
            thumbUpButton.textContent = '👍';
            let thumbDownButton = document.createElement('button');
            thumbDownButton.className = 'thumb-down';
            thumbDownButton.textContent = '👎';
            let deleteButton = document.createElement('button');
            deleteButton.className = 'delete';
            deleteButton.textContent = '❌';
    
            // Append buttons to the button container
            buttonContainer.appendChild(thumbUpButton);
            buttonContainer.appendChild(thumbDownButton);
            buttonContainer.appendChild(deleteButton);
    
            // Append content and the button container to the list item
            listItem.appendChild(contentSpan);
            listItem.appendChild(buttonContainer);
    
            // Append the list item to the list
            resultList.appendChild(listItem);
        });
    
    
        // After the list is populated, attach the event listeners
        attachEventListenersToListItems();
    }

    function fetchUsageCount() {
        fetch('/get-usage-info')
            .then(response => response.json())
            .then(data => {
                // Update the content of the element with the new usage count
                const usageCountElement = document.getElementById('usage-count');
                usageCountElement.textContent = data.usageCount; // Assuming your API returns the usage count in the 'usageCount' field
            })
            .catch(error => {
                console.error('Error fetching usage count:', error);
            });
    }

    
    function attachEventListenersToListItems() {
        document.querySelectorAll('.thumb-up').forEach(button => {
            button.addEventListener('click', function(event) {
                // Handle thumb up action
            });
        });

        document.querySelectorAll('.thumb-down').forEach(button => {
            button.addEventListener('click', function(event) {
                // Handle thumb down action
            });
        });

        document.querySelectorAll('.delete').forEach(button => {
            button.addEventListener('click', function(event) {
                const listItem = event.target.closest('li');
                const entryId = listItem.getAttribute('data-entry-id'); // Make sure to set this data attribute when creating the list items
        
                fetch(`/delete-entry/${entryId}`, {
                    method: 'DELETE'
                })
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        listItem.remove(); // Remove the item from the DOM only if the deletion was successful
                    } else {
                        console.error('Failed to delete the entry');
                    }
                })
                .catch(error => console.error('Error:', error));

                // Get the existing cached data from localStorage
                const cachedData = JSON.parse(localStorage.getItem('latestData'));

                // Remove the deleted entry from the cached data
                const updatedData = cachedData.filter(entry => entry.id !== entryIdToDelete);

                // Update localStorage with the updated data
                localStorage.setItem('latestData', JSON.stringify(updatedData));
                
            });
        });
        
    }
});

