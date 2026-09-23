let fileInputs = document.querySelectorAll('.input-file');

fileInputs.forEach(fileInput => {
    const input = fileInput.querySelector('.input-file__file');
    const inputText = fileInput.querySelector('.input-file__text');

    input.addEventListener('change', function () {
        inputText.innerHTML = this.files[0].name
    })
});