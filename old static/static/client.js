document.addEventListener('DOMContentLoaded', () => {
    // Handle file input change
    document.getElementById('fileInput').addEventListener('change', handleFileInputChange);

    // Trigger file input click when dropdown item is clicked
    document.getElementById('uploadFile').addEventListener('click', function(event) {
        event.preventDefault();
        document.getElementById('fileInput').click();
    });

    // Show the checkbox modal and populate checkboxes
    document.getElementById('showModal').addEventListener('click', showCheckboxModal);

    // Close the checkbox modal
    document.getElementById('closeCheckboxModal').addEventListener('click', closeModal);
    document.getElementById('closeCheckboxModalFooter').addEventListener('click', closeModal);
    document.querySelector('.modal-background').addEventListener('click', closeModal);

    // Collect selected headers and download modified CSV
    document.getElementById('downloadCsv').addEventListener('click', downloadModifiedCsv);

    // Add event listener to the Send Message button
    document.getElementById('sendMessageButton').addEventListener('click', sendMessage);

    // Initialize textarea height on page load
    const textarea = document.querySelector('.textarea');
    autoResize(textarea);
    textarea.addEventListener('input', () => autoResize(textarea));

    // Close dropdown if clicked outside
    document.addEventListener('click', function(event) {
        const dropdown = document.getElementById('uploadDropdown');
        if (!dropdown.contains(event.target)) {
            dropdown.classList.remove('is-active');
        }
    });
});

async function handleFileInputChange(event) {
    const file = event.target.files[0];
    if (file) {
        const formData = new FormData();
        formData.append("file", file);

        // Show loading animation
        showLoader();

        try {
            const response = await fetch("http://localhost:8000/upload_file/", {
                method: "POST",
                body: formData
            });

            const result = await response.json();
            if (response.ok) {
                showModal(result.message);
            } else {
                showModal(result.detail);
            }
        } catch (error) {
            console.error("Error uploading file:", error);
            showModal("Error uploading file. " + error);
        } finally {
            // Hide loading animation
            hideLoader();
        }
    }
}

async function showCheckboxModal(event) {
    event.preventDefault();
    document.getElementById('checkboxModal').classList.add('is-active');

    try {
        const response = await fetch("http://localhost:8000/get_headers_uploaded_csv_file/");
        const result = await response.json();

        if (response.ok) {
            const checkboxContainer = document.querySelector('#checkboxModal .modal-card-body');
            checkboxContainer.innerHTML = ''; // Clear existing checkboxes

            result.headers.forEach(header => {
                const fieldDiv = document.createElement('div');
                fieldDiv.className = 'field';

                const label = document.createElement('label');
                label.className = 'checkbox';

                const input = document.createElement('input');
                input.type = 'checkbox';
                input.value = header;

                label.appendChild(input);
                label.appendChild(document.createTextNode(` ${header}`));
                fieldDiv.appendChild(label);
                checkboxContainer.appendChild(fieldDiv);
            });
        } else {
            console.error("Error fetching headers:", result.detail);
        }
    } catch (error) {
        console.error("Error fetching headers:", error);
    }
}

async function downloadModifiedCsv() {
    const checkboxes = document.querySelectorAll('#checkboxModal .modal-card-body input[type="checkbox"]');
    const selectedHeaders = { headers: {} };

    checkboxes.forEach(checkbox => {
        const key = checkbox.value.trim(); // Remove leading and trailing spaces from the key
        selectedHeaders.headers[key] = checkbox.checked;
    });
  

    try {
        const response = await fetch("http://localhost:8000/download_modified_csv_file/", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify(selectedHeaders)
        });

        if (response.ok) {
            const blob = await response.blob();
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.style.display = 'none';
            a.href = url;
            a.download = 'modified_file.csv';
            document.body.appendChild(a);
            a.click();
            window.URL.revokeObjectURL(url);
        } else {
            const result = await response.json();
            console.error("Error downloading CSV:", result.detail);
        }
    } catch (error) {
        console.error("Error downloading CSV:", error);
    }
}

function showModal(message) {
    document.getElementById('modalContent').innerText = message;
    document.getElementById('responseModal').classList.add('is-active');
}

function closeModal() {
    document.getElementById('responseModal').classList.remove('is-active');
}

function showLoader() {
    document.getElementById('loadingSpinner').style.display = 'block';
}

function hideLoader() {
    document.getElementById('loadingSpinner').style.display = 'none';
}

function renderMessages() {
    const messageList = document.getElementById('messageList');
    messageList.innerHTML = ''; // Clear existing messages
    messages.forEach((msg) => {
        const messageCard = document.createElement('div');
        messageCard.className = 'column is-full';
        messageCard.innerHTML = `
            <div class="card">
                <div class="card-content mb-3">
                    <h2 class="title is-4">${msg.role === 'user' ? 'You' : 'AI'}</h2>
                    <div class="content">${msg.content}</div>
                </div>
            </div>
        `;
        messageList.appendChild(messageCard);
    });
}

async function sendMessage() {
    var textarea = document.getElementById('messageInput');
    var messageContent = textarea.value;
    showLoader(); // Show loader
    // Add user message to messages array
    messages.push({ role: 'user', content: messageContent });
    renderMessages(); // Update the message list UI

    try {
        const response = await fetch("https://openrouter.ai/api/v1/chat/completions", {
            method: "POST",
            headers: {
                "Authorization": "Bearer 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",
                "HTTP-Referer": "YOUR_ACTUAL_SITE_URL", // Replace with your site URL
                "X-Title": "YOUR_ACTUAL_SITE_NAME", // Replace with your site name
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                "model": "meta-llama/llama-3.1-8b-instruct:free",
                "messages": messages // Send all messages
            })
        });

        if (response.ok) {
            const result = await response.json();
            const aiMessage = result.choices[0].message.content; // Adjust this based on your API response

            // Add AI response to messages array
            messages.push({ role: 'ai', content: aiMessage });
            renderMessages(); // Update the message list UI

            textarea.value = ''; // Clear the textarea after sending
            autoResize(textarea); // Adjust textarea height
        } else {
            console.error("Error:", response.status, response.statusText);
        }
    } catch (error) {
        console.error("Error sending message:", error);
    } finally {
        hideLoader(); // Hide loader when done
    }
}

function toggleMenu() {
    var navbar = document.getElementById('navbarBasicExample');
    navbar.classList.toggle('is-active');    
}

function autoResize(textarea) {
    const measureDiv = document.querySelector('.textarea-measure');
    measureDiv.innerText = textarea.value + '\n'; // Add content to the measure div
    textarea.style.height = 'auto'; // Reset height to auto
    textarea.style.height = measureDiv.offsetHeight + 'px'; // Set textarea height to match measure div
}