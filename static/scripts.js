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
        } else {
            resultDiv.textContent = `Error: ${data.detail}`;
        }
    } catch (error) {
        resultDiv.textContent = `Error: ${error.message}`;
    }
});
