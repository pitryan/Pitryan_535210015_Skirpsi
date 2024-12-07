console.log("Script form_upload.js loaded successfully");

// Fungsi untuk menampilkan/menghilangkan tombol Remove
function toggleRemoveButton(input) {
    // Dapatkan tombol Remove yang berada di sebelah input
    const removeButton = input.nextElementSibling;

    // Periksa apakah tombol Remove ditemukan
    if (!removeButton) {
        console.error('Remove button not found for input:', input);
        return;
    }

    if (input.files.length > 0) {
        removeButton.hidden = false; // Tampilkan tombol jika file dipilih
        console.log('File selected. Showing Remove button.');
    } else {
        removeButton.hidden = true; // Sembunyikan tombol jika tidak ada file
        console.log('No file selected. Hiding Remove button.');
    }

    // Hapus pesan feedback jika file baru dipilih
    const feedback = input.closest(".file-upload-group").querySelector(".file-feedback");
    if (feedback) {
        feedback.textContent = ""; // Kosongkan feedback
    } else {
        console.warn('Feedback element not found for input:', input);
    }
}

// Fungsi untuk menghapus file yang dipilih
function removeFile(button) {
    // Dapatkan elemen input file terkait
    const fileInput = button.previousElementSibling;

    if (!fileInput) {
        console.error('File input not found for button:', button);
        return;
    }

    // Reset nilai input file
    fileInput.value = "";

    // Reset label jika ada atribut data-original-text
    const label = button.closest(".file-upload-group").querySelector(".file-label");
    if (label) {
        const originalText = label.getAttribute("data-original-text");
        if (originalText) {
            label.textContent = originalText; // Kembalikan teks label
        }
    } else {
        console.warn('Label not found for button:', button);
    }

    // Sembunyikan tombol Remove
    button.hidden = true;

    // Tampilkan pesan feedback
    const feedback = button.closest(".file-upload-group").querySelector(".file-feedback");
    if (feedback) {
        feedback.textContent = "File telah dihapus.";
        feedback.style.color = "red";
    } else {
        console.warn('Feedback element not found for button:', button);
    }

    console.log('File removed and UI reset.');
}

// Tambahkan listener untuk debugging
document.addEventListener("DOMContentLoaded", function () {
    console.log("DOM fully loaded and parsed.");
    const inputs = document.querySelectorAll(".file-input");
    inputs.forEach(input => {
        console.log("Input file initialized:", input);
        input.addEventListener("change", function () {
            toggleRemoveButton(this);
        });
    });
});
