document.addEventListener('DOMContentLoaded', function() {
    const fileInput = document.getElementById('fileInput');
    const submitButton = document.getElementById('submitButton');

    // Add event listener to file input for changes
    fileInput.addEventListener('change', function() {
        console.log('a')
        if (fileInput.files.length > 0) {
            submitButton.style.display = 'inline';
        } else {
            submitButton.style.display = 'none';
        }
    });
});
