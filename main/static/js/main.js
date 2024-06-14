document.addEventListener('DOMContentLoaded', function() {
    const fileInput = document.getElementById('fileInput');
    const submitButton = document.getElementById('submitButton');
    const countButton = document.getElementById('countButton');

    const imageExtensions = ['jpg', 'jpeg', 'png'];
    const videoExtensions = ['mp4', 'mov', 'avi', 'webm'];

    fileInput.addEventListener('change', function() {
        if (fileInput.files.length > 0) {
            const file = fileInput.files[0];
            const fileExtension = file.name.split('.').pop().toLowerCase();

            if (imageExtensions.includes(fileExtension)) {
                submitButton.style.display = 'inline';
                countButton.style.display = 'none';
            } else if (videoExtensions.includes(fileExtension)) {
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

    submitButton.addEventListener('click', function () {
        document.getElementById('uploadForm').action = '/upload';
    });

    countButton.addEventListener('click', function () {
        document.getElementById('uploadForm').action = '/upload-count';
    });
});
