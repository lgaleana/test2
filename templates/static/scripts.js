document.getElementById('url-form').addEventListener('submit', async function(event) {
    event.preventDefault();
    const urlInput = document.getElementById('url-input').value;
    const resultDiv = document.getElementById('result');
    resultDiv.textContent = 'Loading...';

    try {
        const response = await fetch(`/extract-text?url=${encodeURIComponent(urlInput)}`);
        const data = await response.json();
        if (response.ok) {
            resultDiv.textContent = data.text;

            // Create a div to hold the images
            const imagesDiv = document.createElement('div');
            data.images.forEach(src => {
                const img = document.createElement('img');
                img.src = src;
                img.style.maxWidth = '200px';
                img.style.margin = '10px';
                imagesDiv.appendChild(img);
            });

            // Append the images div to the result div
            resultDiv.appendChild(imagesDiv);
        } else {
            resultDiv.textContent = `Error: ${data.detail}`;
        }
    } catch (error) {
        resultDiv.textContent = `Error: ${error.message}`;
    }
});
