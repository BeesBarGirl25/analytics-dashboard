function openTab(event, tabId) {
    // Reset active class on all tabs
    const tabs = document.querySelectorAll('.tab-link');
    tabs.forEach(tab => tab.classList.remove('active'));

    // Activate the clicked tab
    event.currentTarget.classList.add('active');

    // Hide all content panels
    const tabPanels = document.querySelectorAll('.tab-panel');
    tabPanels.forEach(panel => panel.classList.remove('active'));

    // Show the selected content panel
    const activePanel = document.getElementById(tabId);
    if (activePanel) {
        activePanel.classList.add('active');
    }
}

// Function to update tab labels based on dropdown selection
function updateTabLabels() {
    const dropdown = document.getElementById('match-selection'); // Match dropdown
    const selectedOption = dropdown.options[dropdown.selectedIndex].text; // Get selected teams (e.g., "Team A vs Team B")

    // Split the selected text into teams by the "vs" separator
    const teams = selectedOption.split(' vs ');

    if (teams.length === 2) {
        const [team1, team2] = teams; // Destructure teams array for clarity

        // Update Tab 1
        const tab2 = document.querySelector('.tab-link:nth-child(2)');
        tab2.textContent = team1;
        tab2.setAttribute('data-team', team1);

        // Update Tab 2
        const tab3 = document.querySelector('.tab-link:nth-child(3)');
        tab3.textContent = team2;
        tab3.setAttribute('data-team', team2);

        // (Optional) Update Tab Panel Content
        const panel1 = document.getElementById('Tab2');
        panel1.querySelector('p').textContent = `Content for ${team1}`;

        const panel2 = document.getElementById('Tab3');
        panel2.querySelector('p').textContent = `Content for ${team2}`;
    }
}

// Event listener for dropdown changes
document.getElementById('match-selection').addEventListener('change', updateTabLabels);

// Call the function on page load to set initial tab labels
window.onload = updateTabLabels;
