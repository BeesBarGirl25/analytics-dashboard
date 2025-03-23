function populateDropdown() {
    fetch('/api/get_competitions')
        .then(response => response.json())
        .then(data => {
            const dropdown = document.getElementById('dropdown');
            dropdown.innerHTML = ''; // Clear previous options

            data.forEach(option => {
                const opt = document.createElement('option');
                opt.value = `${option.competition_id}-${option.season_id}`; // Add competition_id and season_id
                opt.textContent = option.display_key; // Add display key
                dropdown.appendChild(opt);
            });
            const defaultOption = dropdown.options[dropdown.selectedIndex];
            const event = new CustomEvent('DropdownPopulated', {
                detail: {
                    competition_id: defaultOption.value.split('-')[0],
                    season_id: defaultOption.value.split('-')[1],
                }
            });
            document.dispatchEvent(event);

            dropdown.addEventListener('change', function () {
                const selectedOption = dropdown.options[dropdown.selectedIndex];
                console.log('Dropdown selection changed:', selectedOption.value);

                const competition_id = selectedOption.value.split('-')[0];
                const season_id = selectedOption.value.split('-')[1];

                // Dispatch the custom event with the new selection details
                const event = new CustomEvent('DropdownPopulated', {
                    detail: { competition_id, season_id }
                });
                document.dispatchEvent(event);
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



