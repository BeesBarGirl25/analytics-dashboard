function updateGraph(selectedMatchId) {
    console.log("Dropdown changed, selectedMatchId:", selectedMatchId); // Debugging log

    fetch('/fetch-data', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ match_id: selectedMatchId }),
    })
    .then(response => {
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        return response.json();
    })
    .then(data => {
        // Validate and use the Plotly figure data
        if (data.fig && data.fig.data && data.fig.layout) {
            console.log("Received figure JSON:", data.fig);
            Plotly.react('graph-div', data.fig.data, data.fig.layout);
        } else {
            console.error("Invalid figure JSON received:", data);
            document.getElementById('graph-div').innerHTML = '<p style="color: red;">Unable to load graph. Please try again.</p>';
        }
    })
    .catch(error => {
        console.error("Error updating graph:", error);
        alert("An error occurred while updating the graph. Please try again.");
    });

}



// Add event listener to the dropdown
document.getElementById('match-selection').addEventListener('change', function () {
    const selectedMatchId = this.value; // Get the selected match ID
    updateGraph(selectedMatchId); // Trigger graph update
});

document.addEventListener("DOMContentLoaded", function() {
    Plotly.Plots.resize('graph-div');
});
