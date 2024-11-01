document.addEventListener('DOMContentLoaded', () => {
  const form = document.getElementById('converter-form');
  const urlInput = document.getElementById('youtube-url');
  const errorMessage = document.getElementById('error-message');

  form.addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const url = urlInput.value.trim();
    if (!url) {
      showError('Please enter a YouTube URL');
      return;
    }

    if (!isValidYouTubeUrl(url)) {
      showError('Please enter a valid YouTube URL');
      return;
    }

    const format = document.querySelector('input[name="format"]:checked').value;
    
    try {
      const formData = new FormData();
      formData.append('url', url);
      formData.append('format', format);

      const response = await fetch('/convert', {
        method: 'POST',
        body: formData
      });

      if (response.ok) {
        const blob = await response.blob();
        const downloadUrl = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.style.display = 'none';
        a.href = downloadUrl;
        a.download = `converted_file.${format}`;
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(downloadUrl);
      } else {
        const errorData = await response.json();
        showError(errorData.error || 'Conversion failed');
      }
    } catch (error) {
      console.error('Error:', error);
      showError('An error occurred during conversion');
    }
    
    // Clear any previous error messages
    hideError();
  });

  function showError(message) {
    errorMessage.textContent = message;
    errorMessage.classList.remove('hidden');
  }

  function hideError() {
    errorMessage.textContent = '';
    errorMessage.classList.add('hidden');
  }

  function isValidYouTubeUrl(url) {
    const youtubeRegex = /^(https?:\/\/)?(www\.)?(youtube\.com|youtu\.?be)\/.+$/;
    return youtubeRegex.test(url);
  }
});