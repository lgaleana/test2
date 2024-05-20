document.getElementById('url-form').addEventListener('submit', async function(event) {
    event.preventDefault();
    const urlInput = document.getElementById('url-input').value;
    const resultDiv = document.getElementById('result');
    resultDiv.textContent = 'Loading...';

    try {
        const response = await fetch(`/extract-text?url=${encodeURIComponent(urlInput)}`);
        const data = await response.json();
        if (response.ok) {
            resultDiv.innerHTML = `<pre>${data.text}</pre>`;
            data.headlines.forEach(item => {
                const img = document.createElement('img');
                img.src = item.image_url;
                const headline = document.createElement('p');
                headline.textContent = item.headline;
                resultDiv.appendChild(img);
                resultDiv.appendChild(headline);
            });
        } else {
            resultDiv.textContent = `Error: ${data.detail}`;
        }
    } catch (error) {
        resultDiv.textContent = `Error: ${error.message}`;
    }
});
