document.getElementById('url-form').addEventListener('submit', async function(event) {
    event.preventDefault();
    const urlInput = document.getElementById('url-input').value;
    const imageResultDiv = document.getElementById('image-result');
    const cropContainer = document.getElementById('crop-container');
    const cropImage = document.getElementById('crop-image');
    const cropButton = document.getElementById('crop-button');
    const loadingIndicator = document.getElementById('loading-indicator');
    let cropper;
    let currentImageContainer; // To keep track of the current image container being cropped

    imageResultDiv.innerHTML = ''; // Clear previous images
    loadingIndicator.style.display = 'block'; // Show loading indicator
    console.log("Loading indicator shown");

    try {
        const response = await fetch(`/extract-text?url=${encodeURIComponent(urlInput)}`);
        const data = await response.json();
        if (response.ok) {
            // Display images and headlines
            data.images.forEach((src, index) => {
                const container = document.createElement('div');
                container.classList.add('image-container');

                const imageWrapper = document.createElement('div');
                imageWrapper.classList.add('image-wrapper');

                const img = document.createElement('img');
                img.src = `/fetch-image?url=${encodeURIComponent(src)}`;
                img.alt = 'Extracted image';
                img.style.maxWidth = '100%';
                imageWrapper.appendChild(img);

                const headline = document.createElement('p');
                headline.textContent = data.headlines[index];
                headline.classList.add('draggable');
                headline.setAttribute('data-x', 10); // Set initial x position
                headline.setAttribute('data-y', 10); // Set initial y position
                headline.setAttribute('contenteditable', 'true'); // Make the text editable
                headline.style.backgroundColor = 'transparent'; // Ensure no background
                headline.style.fontSize = '20px'; // Set default font size
                imageWrapper.appendChild(headline);

                container.appendChild(imageWrapper);

                const fontSizeLabel = document.createElement('label');
                fontSizeLabel.setAttribute('for', 'font-size');
                fontSizeLabel.textContent = 'Font Size:';
                container.appendChild(fontSizeLabel);

                const fontSizeInput = document.createElement('input');
                fontSizeInput.setAttribute('type', 'number');
                fontSizeInput.setAttribute('id', 'font-size');
                fontSizeInput.setAttribute('name', 'font-size');
                fontSizeInput.setAttribute('value', '20');
                fontSizeInput.setAttribute('min', '10');
                fontSizeInput.setAttribute('max', '100');
                container.appendChild(fontSizeInput);

                // Add event listener to update font size in real-time
                fontSizeInput.addEventListener('input', () => {
                    headline.style.fontSize = `${fontSizeInput.value}px`;
                });

                // Add color picker
                const colorLabel = document.createElement('label');
                colorLabel.setAttribute('for', 'font-color');
                colorLabel.textContent = 'Font Color:';
                container.appendChild(colorLabel);

                const colorInput = document.createElement('input');
                colorInput.setAttribute('type', 'color');
                colorInput.setAttribute('id', 'font-color');
                colorInput.setAttribute('name', 'font-color');
                colorInput.setAttribute('value', '#000000'); // Default to black
                container.appendChild(colorInput);

                // Add event listener to update font color in real-time
                colorInput.addEventListener('input', () => {
                    headline.style.color = colorInput.value;
                });

                // Add font type selection
                const fontTypeLabel = document.createElement('label');
                fontTypeLabel.setAttribute('for', 'font-type');
                fontTypeLabel.textContent = 'Font Type:';
                container.appendChild(fontTypeLabel);

                const fontTypeInput = document.createElement('select');
                fontTypeInput.setAttribute('id', 'font-type');
                fontTypeInput.setAttribute('name', 'font-type');
                ['Arial', 'Courier_New', 'Verdana'].forEach(font => {
                    const option = document.createElement('option');
                    option.value = font;
                    option.textContent = font.replace('_', ' ');
                    fontTypeInput.appendChild(option);
                });
                container.appendChild(fontTypeInput);

                // Add event listener to update font type in real-time
                fontTypeInput.addEventListener('change', () => {
                    headline.style.fontFamily = fontTypeInput.value.replace('_', ' ');
                });

                const cropButton = document.createElement('button');
                cropButton.textContent = 'Crop';
                cropButton.addEventListener('click', () => {
                    cropImage.src = `/fetch-image?url=${encodeURIComponent(src)}`;
                    cropContainer.style.display = 'block';
                    cropper = new Cropper(cropImage, {
                        aspectRatio: 16 / 9,
                        viewMode: 1,
                    });
                    currentImageContainer = container; // Set the current image container
                });
                container.appendChild(cropButton);

                const downloadButton = document.createElement('button');
                downloadButton.textContent = 'Download';
                downloadButton.addEventListener('click', () => {
                    headline.style.pointerEvents = 'none'; // Disable pointer events on the headline
                    const imageElement = container.querySelector('img');
                    downloadImage(imageElement, headline.textContent, headline, fontSizeInput.value, colorInput.value, fontTypeInput.value);
                });
                container.appendChild(downloadButton);

                imageResultDiv.appendChild(container);

                // Add logging to check positions and dimensions
                console.log("Headline position and dimensions:", headline.getBoundingClientRect());
                console.log("Download button position and dimensions:", downloadButton.getBoundingClientRect());
            });

            // Initialize interact.js for drag-and-drop
            interact('.draggable').draggable({
                modifiers: [
                    interact.modifiers.restrictRect({
                        restriction: '.image-wrapper', // Restrict to the image wrapper
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
    } finally {
        loadingIndicator.style.display = 'none'; // Hide loading indicator
        console.log("Loading indicator hidden");
    }

    cropButton.addEventListener('click', () => {
        const croppedCanvas = cropper.getCroppedCanvas();
        croppedCanvas.toBlob((blob) => {
            const croppedImageURL = URL.createObjectURL(blob);
            
            // Display the cropped image
            const croppedImage = document.createElement('img');
            croppedImage.src = croppedImageURL;
            croppedImage.alt = 'Cropped image';
            croppedImage.style.maxWidth = '100%';

            // Replace the original image with the cropped image in the current image container
            const originalImage = currentImageContainer.querySelector('img');
            originalImage.src = croppedImageURL;
            originalImage.dataset.blob = croppedImageURL; // Store the blob URL for download

            cropContainer.style.display = 'none';
            cropper.destroy();
        }, 'image/png');
    });
});
