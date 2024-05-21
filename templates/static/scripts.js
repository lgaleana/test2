document.getElementById('url-form').addEventListener('submit', async function(event) {
    event.preventDefault();
    const urlInput = document.getElementById('url-input').value;
    const imageResultDiv = document.getElementById('image-result');
    
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

                        // Ensure the text cannot be dragged outside the image frame
                        const parentRect = target.parentElement.getBoundingClientRect();
                        const targetRect = target.getBoundingClientRect();

                        if (targetRect.left + event.dx < parentRect.left) {
                            event.dx = parentRect.left - targetRect.left;
                        }
                        if (targetRect.top + event.dy < parentRect.top) {
                            event.dy = parentRect.top - targetRect.top;
                        }
                        if (targetRect.right + event.dx > parentRect.right) {
                            event.dx = parentRect.right - targetRect.right;
                        }
                        if (targetRect.bottom + event.dy > parentRect.bottom) {
                            event.dy = parentRect.bottom - targetRect.bottom;
                        }

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
});
