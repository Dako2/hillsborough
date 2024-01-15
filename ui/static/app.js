// static/app.js
document.addEventListener('DOMContentLoaded', function() {
    const messageBox = document.getElementById('message-box');
    const messageInput = document.getElementById('message-input');
    const sendButton = document.getElementById('send-button');
    // Update the footer with the current year
    document.getElementById('year').textContent = new Date().getFullYear();

    // Handle the tea recommendation form submission
    document.getElementById('tea-form').addEventListener('submit', function(event) {
        // Prevent the default form submission behavior
        event.preventDefault();

        // Get the value of the symptoms input
        var symptoms = document.getElementById('symptoms').value;

        // For demonstration purposes, just display the symptoms in the result div
        // In a real application, you would send this data to the server for processing
        document.getElementById('result').textContent = 'Tea recommendation for: ' + symptoms;
    });
    
    sendButton.addEventListener('click', sendMessage);

    function sendMessage() {
        const message = messageInput.value.trim();
        if (message !== '') {
            // Add message to the UI
            messageBox.innerHTML += '<p>You: ' + message + '</p>';
            
            // Clear input field
            messageInput.value = '';

            // Send message to the server
            fetch('/send_message', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    message: message
                })
            });
        }
    }

    // Function to retrieve and display messages from the server
    function displayMessages() {
        fetch('/get_messages')
            .then(response => response.json())
            .then(data => {
                data.forEach(message => {
                    messageBox.innerHTML += '<p>Other: ' + message + '</p>';
                });
            });
    }

    // Poll for new messages every few seconds
    setInterval(displayMessages, 3000);

    // Display initial messages
    displayMessages();
});

