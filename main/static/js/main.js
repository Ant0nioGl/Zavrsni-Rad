document.addEventListener('DOMContentLoaded', function() {
    const fileInput = document.getElementById('fileInput');
    const submitButton = document.getElementById('submitButton');
    const countButton = document.getElementById('countButton');

    // Define allowed file extensions for images and videos
    const allowedImageExtensions = ['jpg', 'jpeg', 'png'];
    const allowedVideoExtensions = ['mp4', 'mov', 'avi', 'webm'];

    // Add event listener to file input for changes
    fileInput.addEventListener('change', function() {
        if (fileInput.files.length > 0) {
            const file = fileInput.files[0];
            const fileExtension = file.name.split('.').pop().toLowerCase();

            if (allowedImageExtensions.includes(fileExtension)) {
                submitButton.style.display = 'inline';
                countButton.style.display = 'none';
            } else if (allowedVideoExtensions.includes(fileExtension)) {
                submitButton.style.display = 'inline';
                countButton.style.display = 'inline';
            } else {
                submitButton.style.display = 'none';
                countButton.style.display = 'none';
            }
        } else {
            submitButton.style.display = 'none';
            countButton.style.display = 'none';
        }
    });

    // Set form action to /upload when submitButton is clicked
    submitButton.addEventListener('click', function () {
        document.getElementById('uploadForm').action = '/upload';
    });

    // Set form action to /upload-count when countButton is clicked
    countButton.addEventListener('click', function () {
        document.getElementById('uploadForm').action = '/upload-count';
    });
});
