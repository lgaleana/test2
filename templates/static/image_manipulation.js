async function downloadImage(imageElement, text, headlineElement, fontSize) {
    const x = parseFloat(headlineElement.getAttribute('data-x')) || 0;
    const y = parseFloat(headlineElement.getAttribute('data-y')) || 0;
    const imageUrl = imageElement.dataset.blob || imageElement.src;

    const response = await fetch(imageUrl);
    const blob = await response.blob();

    const formData = new FormData();
    formData.append('image', blob, 'cropped_image.png');
    formData.append('text', text);
    formData.append('x', x);
    formData.append('y', y);
    formData.append('font_size', fontSize); // Include the font size

    const downloadResponse = await fetch('/download-image', {
        method: 'POST',
        body: formData
    });

    if (downloadResponse.ok) {
        const downloadBlob = await downloadResponse.blob();
        const url = window.URL.createObjectURL(downloadBlob);
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