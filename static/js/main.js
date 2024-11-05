function isVideoUrl(url) {
    var videoUrlPatterns = [
        /^https?:\/\/(www\.)?youtube\.com\/watch\?v=/,
        /^https?:\/\/youtu\.be\//,
    ];
    for (var i = 0; i < videoUrlPatterns.length; i++) {
        if (videoUrlPatterns[i].test(url)) {
            return true;
        }
    }
    return false;
}

document.addEventListener('DOMContentLoaded', function () {
    // Check if we're on the download progress page
    if (document.getElementById('log-container')) {
        let fixedHeaders = [];

        // Function to fetch and update log messages
        function updateLogMessages() {
            fetch('/progress')
                .then(response => response.json())
                .then(data => {
                    const logContainer = document.getElementById('log-messages');
                    logContainer.innerHTML = '';  // Clear previous log messages

                    // Update fixed headers dynamically based on the first log messages
                    if (fixedHeaders.length === 0 && data.log_messages.length >= 4) {
                        fixedHeaders = data.log_messages.slice(0, 4); // Set the first 4 messages as fixed headers
                    }

                    // Display the fixed headers at the top
                    fixedHeaders.forEach(header => {
                        const headerEntry = document.createElement('div');
                        headerEntry.className = 'log-header';
                        headerEntry.textContent = header;
                        logContainer.appendChild(headerEntry);
                    });

                    // Display the remaining log messages, starting numbering from 1
                    data.log_messages.slice(4).forEach((message, index) => {
                        const logEntry = document.createElement('div');
                        logEntry.className = 'log-entry';
                        logEntry.textContent = `${index + 1}. ${message}`;
                        logContainer.appendChild(logEntry);
                    });

                    // Stop updating if download is complete
                    if (data.log_messages.includes("Download completed.")) {
                        clearInterval(logUpdateInterval);
                    }
                })
                .catch(error => console.error('Error fetching log messages:', error));
        }

        // Update log messages every 1 second
        const logUpdateInterval = setInterval(updateLogMessages, 1000);
    }

    // Existing code for the download form
    const downloadForm = document.getElementById('download-form');
    if (downloadForm) {
        downloadForm.addEventListener('submit', function (event) {
            // Show the loading spinner and progress bar
            document.getElementById('loading-spinner').style.display = 'block';
            // Optionally disable the submit button to prevent multiple submissions
            this.querySelector('button[type="submit"]').disabled = true;
        });
    }

    // Existing code for hiding the months selection
    var channelInput = document.getElementById('channel_input');
    var monthsDiv = document.getElementById('monthsDiv');

    if (channelInput && monthsDiv) {
        channelInput.addEventListener('input', function () {
            var url = channelInput.value.trim();
            if (isVideoUrl(url)) {
                monthsDiv.style.display = 'none';
            } else {
                monthsDiv.style.display = 'block';
            }
        });
    }
});

// Confirmation prompt for deleting scripts
function confirmDeletion() {
    return confirm('Are you sure you want to delete the selected scripts?');
}