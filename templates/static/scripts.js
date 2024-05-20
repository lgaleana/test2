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
                const container = document.createElement('div');
                container.classList.add('image-container');

                const img = document.createElement('img');
                img.src = src;
                img.alt = 'Extracted image';
                img.style.maxWidth = '100%';
                container.appendChild(img);

                const headline = document.createElement('p');
                headline.textContent = data.headlines[index];
                headline.classList.add('draggable');
                container.appendChild(headline);

                imageResultDiv.appendChild(container);
            });

            // Initialize interact.js for drag-and-drop
            interact('.draggable').draggable({
                listeners: {
                    move(event) {
                        const target = event.target;
                        const x = (parseFloat(target.getAttribute('data-x')) || 0) + event.dx;
                        const y = (parseFloat(target.getAttribute('data-y')) || 0) + event.dy;

                        target.style.transform = `translate(${x}px, ${y}px)`;
                        target.setAttribute('data-x', x);
                        target.setAttribute('data-y', y);
                    }
                }
            });
        } else {
            textResultDiv.textContent = `Error: ${data.detail}`;
        }
    } catch (error) {
        textResultDiv.textContent = `Error: ${error.message}`;
    }
});
