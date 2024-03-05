var toggleButtons = document.getElementsByClassName('toggleButton');
var balanceElements = document.getElementsByClassName('balance');
var originalBalances = [];

window.onload = function() {
    for (var i = 0; i < balanceElements.length; i++) {
        originalBalances[i] = balanceElements[i].innerText; // Update the original balance when the page loads
    }
};

function toggleBalance(i) {
    // Toggle the balance for the i-th element
    if (balanceElements[i].innerText == '*****') {
        balanceElements[i].innerText = originalBalances[i]; // Show the balance
    } else {
        originalBalances[i] = balanceElements[i].innerText; // Update the original balance before hiding it
        balanceElements[i].innerText = '*****'; // Hide the balance
    }
}

for (var i = 0; i < toggleButtons.length; i++) {
    (function(i) {
        toggleButtons[i].addEventListener('click', function() {
            toggleBalance(i);
        });
    })(i);
}
