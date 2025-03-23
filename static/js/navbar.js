function populateDropdown() {
    fetch('/api/get_competitions')
        .then(response => response.json())
        .then(data => {
            const dropdownList = document.getElementById('dropdownList');
            const selectedItem = document.getElementById('selectedItem');
            dropdownList.innerHTML = ''; // Clear previous options

            // Group data by competition_name
            const groupedData = data.reduce((groups, item) => {
                const { competition_name, competition_id, season_id, display_key } = item;
                if (!groups[competition_name]) {
                    groups[competition_name] = [];
                }
                groups[competition_name].push({ competition_id, season_id, display_key });
                return groups;
            }, {});

            // Populate the dropdown list
            Object.entries(groupedData).forEach(([competitionName, seasons]) => {
                // Create competition div
                const competitionDiv = document.createElement('div');
                competitionDiv.className = 'competition';
                competitionDiv.textContent = competitionName;

                // Create season list (nested)
                const seasonList = document.createElement('div');
                seasonList.className = 'season-list';

                seasons.forEach(({ competition_id, season_id, display_key }) => {
                    const seasonDiv = document.createElement('div');
                    seasonDiv.className = 'season';
                    seasonDiv.textContent = display_key;
                    seasonDiv.dataset.competitionId = competition_id;
                    seasonDiv.dataset.seasonId = season_id;

                    // Handle season selection
                    seasonDiv.addEventListener('click', function () {
                        selectedItem.textContent = display_key; // Update the selected item text
                        dropdownList.style.display = 'none'; // Collapse the dropdown

                        console.log(`Selected: Competition ID ${competition_id}, Season ID ${season_id}`);

                        // Dispatch a custom event
                        const event = new CustomEvent('DropdownPopulated', {
                            detail: {
                                competition_id: seasonDiv.dataset.competitionId,
                                season_id: seasonDiv.dataset.seasonId,
                            },
                        });
                        document.dispatchEvent(event);
                    });

                    seasonList.appendChild(seasonDiv);
                });

                // Toggle season list visibility on competition click
                competitionDiv.addEventListener('click', function () {
                    const isVisible = seasonList.style.display === 'block';
                    seasonList.style.display = isVisible ? 'none' : 'block'; // Toggle visibility
                });

                dropdownList.appendChild(competitionDiv);
                dropdownList.appendChild(seasonList);
            });

            // Expand/collapse dropdown when the selected item is clicked
            selectedItem.addEventListener('click', function () {
                const isVisible = dropdownList.style.display === 'block';
                dropdownList.style.display = isVisible ? 'none' : 'block';
            });
        })
        .catch(error => {
            console.error('Error fetching dropdown options:', error);
        });
}

// Initialize dropdown population on page load
document.addEventListener('DOMContentLoaded', populateDropdown);




function toggleSidebar() {
    const sidebar = document.getElementById("mySidebar");
    const arrow = document.getElementById("toggleArrow");
    const mainContent = document.getElementById("main");

    if (sidebar.style.width === "250px") {
        // Collapse the sidebar
        sidebar.style.width = "0";
        mainContent.style.marginLeft = "0";
        arrow.classList.remove("open"); // Reset arrow rotation
    } else {
        // Expand the sidebar
        sidebar.style.width = "250px";
        mainContent.style.marginLeft = "250px";
        arrow.classList.add("open"); // Rotate arrow
    }
}



