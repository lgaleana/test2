async function downloadImage(imageElement, text, headlineElement, fontSize, color, fontType) {
    const x = parseFloat(headlineElement.getAttribute('data-x')) || 0;
    const y = parseFloat(headlineElement.getAttribute('data-y')) || 0;
    const imageUrl = imageElement.dataset.blob || imageElement.src;
    const headline = headlineElement.textContent.trim();  // Get the headline text

    // Log the coordinates and dimensions
    console.log(`Text: ${text}, X: ${x}, Y: ${y}, Font Size: ${fontSize}, Color: ${color}, Font Type: ${fontType}`);
    console.log(`Image URL: ${imageUrl}`);
    console.log(`Headline: ${headline}`);
    console.log(`Headline dimensions: ${headlineElement.getBoundingClientRect()}`);
    console.log(`Image dimensions: ${imageElement.getBoundingClientRect()}`);
    console.log(`Image size: Width: ${imageElement.naturalWidth}, Height: ${imageElement.naturalHeight}`);

    const response = await fetch(imageUrl);
    const blob = await response.blob();

    const formData = new FormData();
    formData.append('image', blob, 'cropped_image.png');
    formData.append('text', text);
    formData.append('x', x);
    formData.append('y', y);
    formData.append('font_size', fontSize); // Include the font size
    formData.append('color', color); // Include the color
    formData.append('font_type', fontType); // Include the font type
    formData.append('headline', headline); // Include the headline

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
        a.download = `${headline}.png`;  // Use the headline as the filename
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);

        // Re-enable pointer events on the headline after download
        headlineElement.style.pointerEvents = 'auto';
    } else {
        alert('Failed to download image');
    }
}
