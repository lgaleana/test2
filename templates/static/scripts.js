document.getElementById('url-form').addEventListener('submit', async function(event) {
    event.preventDefault();
    const urlInput = document.getElementById('url-input').value;
    const textResultDiv = document.getElementById('text-result');
    const imageResultDiv = document.getElementById('image-result');
    const resultDiv = document.getElementById('result');
    
    textResultDiv.textContent = 'Loading...';
    imageResultDiv.innerHTML = ''; // Clear previous images

    try {
        const response = await fetch(`/extract-text?url=${encodeURIComponent(urlInput)}`);
        const data = await response.json();
        if (response.ok) {
            textResultDiv.textContent = data.text;

            // Display images and headlines
            data.images.forEach((src, index) => {
                const img = document.createElement('img');
                img.src = src;
                img.alt = 'Extracted image';
                img.style.maxWidth = '100%';
                img.style.margin = '10px 0';
                imageResultDiv.appendChild(img);

                const headline = document.createElement('p');
                headline.textContent = data.headlines[index];
                headline.style.fontWeight = 'bold';
                imageResultDiv.appendChild(headline);
            });
        } else {
            textResultDiv.textContent = `Error: ${data.detail}`;
        }
    } catch (error) {
        textResultDiv.textContent = `Error: ${error.message}`;
    }
});
