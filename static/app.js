let html5QrcodeScanner; // Declare the scanner globally

function onScanSuccess(qrMessage) {
    // Show loading message
    document.getElementById("loading-message").style.display = "block";

    // Send QR code data to the server
    console.log(`QR matched = ${qrMessage}`);
    const url = new URL(window.location.origin + '/attendance');
    url.searchParams.append('employee_id', qrMessage);

    fetch(url)
        .then(response => response.json())
        .then(data => {
            const resultContainer = document.getElementById("qr-reader-results");
            resultContainer.innerHTML = `<p>${data.message}</p>`;
        })
        .catch(err => {
            console.error(`Fetch error: ${err}`);
            const resultContainer = document.getElementById("qr-reader-results");
            resultContainer.innerHTML = `<p>Error: ${err.message}</p>`;
        })
        .finally(() => {
            document.getElementById("loading-message").style.display = "none";
            stopScanner(); // Stop the scanner after successful read
        });
}

function onScanFailure(error) {
    console.warn(`QR Code scan error = ${error}`);
}

function startScanner() {
    html5QrcodeScanner = new Html5QrcodeScanner(
        "reader", { fps: 10, qrbox: 250 });
    html5QrcodeScanner.render(onScanSuccess, onScanFailure);
}

function stopScanner() {
    if (html5QrcodeScanner) {
        html5QrcodeScanner.clear().then(() => {
            console.log("QR Code Scanner stopped.");
        }).catch(err => {
            console.warn("Failed to clear html5QrcodeScanner, error: " + err);
        });
    }
}

window.addEventListener('load', startScanner);