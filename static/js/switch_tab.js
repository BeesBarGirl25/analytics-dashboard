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

        // Update Tab 2 (Team 1)
        const tab2 = document.querySelector('.tab-link:nth-child(2)');
        tab2.textContent = team1;
        tab2.setAttribute('data-team', team1);

        // Update Tab 3 (Team 2)
        const tab3 = document.querySelector('.tab-link:nth-child(3)');
        tab3.textContent = team2;
        tab3.setAttribute('data-team', team2);
    }
}

// Event listener for dropdown changes
document.getElementById('match-selection').addEventListener('change', updateTabLabels);

// Call the function on page load to set initial tab labels
window.onload = updateTabLabels;

document.querySelectorAll('.tab-link').forEach(tab => {
    tab.addEventListener('click', function () {
        const matchDropdown = document.getElementById('match-selection'); // Get dropdown
        const matchId = matchDropdown.value; // Get selected match ID
        const teamName = this.getAttribute('data-team'); // Get team name from tab

        fetch('/filter-team', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ match_id: matchId, team_name: teamName })
        })
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            const sharedContent = document.getElementById('shared-content-placeholder');
            sharedContent.innerHTML = ""; // Clear existing placeholder content

            if (data.categorized) {
                // Add a collapsible section for "Squad"
                const collapsibleSection = `
                    <div class="collapsible-section">
                        <div class="collapsible" id="squad-header">
                            <span>Squad</span>
                            <span class="arrow">&#x25BC;</span>
                        </div>
                        <div class="collapsible-content" id="squad-section">
                            <div id="team-categorized-container">
                            </div>
                        </div>
                    </div>
                `;
                sharedContent.innerHTML = collapsibleSection;

                // Add event listener for the collapsible section
                document.getElementById('squad-header').addEventListener('click', function () {
                    const content = document.getElementById('squad-section');
                    content.classList.toggle('show');

                    const arrow = this.querySelector('.arrow');
                    arrow.textContent = content.classList.contains('show') ? '\u25B2' : '\u25BC'; // Up or down arrow
                });

                // Generate and append a table for categorized players
                const tableContainer = document.getElementById('team-categorized-container');
                const table = document.createElement('table');
                table.classList.add('categorized-table');

                // Create table headers
                const headers = Object.keys(data.categorized);
                const headerRow = document.createElement('tr');
                headers.forEach(header => {
                    const th = document.createElement('th');
                    th.textContent = header;
                    headerRow.appendChild(th);
                });
                table.appendChild(headerRow);

                // Create table rows
                const numRows = Math.max(...Object.values(data.categorized).map(arr => arr.length));
                for (let i = 0; i < numRows; i++) {
                    const row = document.createElement('tr');
                    headers.forEach(header => {
                        const td = document.createElement('td');
                        const value = data.categorized[header][i];
                        td.textContent = value === null || value === "NaN" ? "N/A" : value; // Handle null values
                        row.appendChild(td);
                    });
                    table.appendChild(row);
                }

                tableContainer.appendChild(table); // Add the table to the container
            }

            if (data.unmatched && data.unmatched.length > 0) {
                console.warn("Unmatched positions:", data.unmatched);
            }
        })
        .catch(error => {
            console.error("Error fetching filtered team data:", error);
            alert("An error occurred while fetching team data. Please try again.");
        });
    });
});
