document.getElementById('url-form').addEventListener('submit', async function(event) {
    event.preventDefault();
    const urlInput = document.getElementById('url-input').value;
    const imageResultDiv = document.getElementById('image-result');
    const cropContainer = document.getElementById('crop-container');
    const cropImage = document.getElementById('crop-image');
    const cropButton = document.getElementById('crop-button');
    let cropper;

    imageResultDiv.innerHTML = ''; // Clear previous images

    try {
        const response = await fetch(`/extract-text?url=${encodeURIComponent(urlInput)}`);
        const data = await response.json();
        if (response.ok) {
            // Display images and headlines
            data.images.forEach((src, index) => {
                const container = document.createElement('div');
                container.classList.add('image-container');

                const img = document.createElement('img');
                img.src = `/fetch-image?url=${encodeURIComponent(src)}`;
                img.alt = 'Extracted image';
                img.style.maxWidth = '100%';
                container.appendChild(img);

                const headline = document.createElement('p');
                headline.textContent = data.headlines[index];
                headline.classList.add('draggable');
                headline.setAttribute('data-x', 10); // Set initial x position
                headline.setAttribute('data-y', 10); // Set initial y position
                container.appendChild(headline);

                const cropButton = document.createElement('button');
                cropButton.textContent = 'Crop';
                cropButton.addEventListener('click', () => {
                    cropImage.src = `/fetch-image?url=${encodeURIComponent(src)}`;
                    cropContainer.style.display = 'block';
                    cropper = new Cropper(cropImage, {
                        aspectRatio: 16 / 9,
                        viewMode: 1,
                    });
                });
                container.appendChild(cropButton);

                const downloadButton = document.createElement('button');
                downloadButton.textContent = 'Download';
                downloadButton.addEventListener('click', () => {
                    headline.style.pointerEvents = 'none'; // Disable pointer events on the headline
                    downloadImage(src, data.headlines[index], headline);
                });
                container.appendChild(downloadButton);

                imageResultDiv.appendChild(container);
            });

            // Initialize interact.js for drag-and-drop
            interact('.draggable').draggable({
                modifiers: [
                    interact.modifiers.restrict({
                        restriction: 'parent',
                        endOnly: true,
                        elementRect: { top: 0, left: 0, bottom: 1, right: 1 }
                    })
                ],
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
            imageResultDiv.textContent = `Error: ${data.detail}`;
        }
    } catch (error) {
        imageResultDiv.textContent = `Error: ${error.message}`;
    }

    cropButton.addEventListener('click', () => {
        const croppedCanvas = cropper.getCroppedCanvas();
        const croppedImageURL = croppedCanvas.toDataURL('image/png');
        cropImage.src = croppedImageURL;
        cropContainer.style.display = 'none';
        cropper.destroy();
    });
});

async function downloadImage(imageUrl, text, headlineElement) {
    const x = parseFloat(headlineElement.getAttribute('data-x')) || 0;
    const y = parseFloat(headlineElement.getAttribute('data-y')) || 0;

    const response = await fetch('/download-image', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ image_url: imageUrl, text: text, x: x, y: y })
    });

    if (response.ok) {
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.style.display = 'none';
        a.href = url;
        a.download = 'overlayed_image.png';
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);

        // Re-enable pointer events on the headline after download
        headlineElement.style.pointerEvents = 'auto';
    } else {
        alert('Failed to download image');
    }
}
