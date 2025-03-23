document.addEventListener('DOMContentLoaded', function () {
    // Listen for the custom event dispatched by the top dropdown
    document.addEventListener('DropdownPopulated', function (event) {
        const { competition_id, season_id } = event.detail; // Extract the competition_id and season_id
        console.log(`Received Competition ID: ${competition_id}, Season ID: ${season_id}`);
        populateMatchesDropdown(competition_id, season_id); // Populate match dropdown
    });

    // Listen for the custom event dispatched by the match dropdown
    document.addEventListener('MatchDropdownPopulated', function (event) {
        const { match_id } = event.detail; // Extract the match_id
        console.log(`Received Match ID: ${match_id}`);

        // Trigger both match data and graph fetching
        getMatchData(match_id);
        getMatchGraph(match_id);
    });
});

function populateMatchesDropdown(competition_id, season_id) {
    // Fetch matches from the backend
    fetch('/fetch_matches', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ competition_id, season_id }), // Send both values to the server
    })
        .then(response => response.json())
        .then(data => {
            // Populate the match dropdown
            const matchDropdown = document.getElementById('matchDropdown');
            matchDropdown.innerHTML = ''; // Clear any existing options

            data.forEach(match => {
                const opt = document.createElement('option');
                opt.value = match.value; // Use match_id as value
                opt.textContent = match.text; // Use "Team A vs Team B" as text
                matchDropdown.appendChild(opt);
            });

            // Attach change event listener to the dropdown after populating options
            matchDropdown.addEventListener('change', function () {
                const selectedOption = matchDropdown.options[matchDropdown.selectedIndex];
                const match_id = selectedOption.value;
                console.log('Match dropdown changed, fetching graph for match_id:', match_id);

                // Dispatch the event and trigger data and graph fetching
                const event = new CustomEvent('MatchDropdownPopulated', {
                    detail: { match_id }
                });
                document.dispatchEvent(event);
            });

            // Trigger fetching for the default selected match
            const defaultOption = matchDropdown.options[matchDropdown.selectedIndex];
            if (defaultOption) {
                const match_id = defaultOption.value;
                console.log('Fetching graph for default match_id:', match_id);

                // Dispatch the event and trigger data and graph fetching
                const event = new CustomEvent('MatchDropdownPopulated', {
                    detail: { match_id }
                });
                document.dispatchEvent(event);
            } else {
                console.error('No default option selected in matchDropdown');
            }
        })
        .catch(error => {
            console.error('Error fetching matches:', error);
            const matchDropdown = document.getElementById('matchDropdown');
            matchDropdown.innerHTML = '<option disabled>Error loading matches</option>';
        });
}

function getMatchData(match_id) {
    // Fetch match data from the backend
    console.log('Match ID being sent:', match_id);
    match_id = parseInt(match_id);
    fetch('/fetch_match', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ match_id }), // Send match_id to the server
    })
        .then(response => response.json())
        .then(data => {
            console.log('Received match data:', data);

            // Handle the match data (further processing or UI updates can be added here)
        })
        .catch(error => {
            console.error('Error fetching match data:', error);
        });
}

function getMatchGraph(match_id) {
    const graphContainer = document.getElementById('match-graph-container');

    // Measure the dimensions of the container
    const containerWidth = graphContainer.clientWidth;
    const containerHeight = graphContainer.clientHeight;

    console.log('Container dimensions:', containerWidth, containerHeight);

    fetch('/fetch_match_graph', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ match_id, width: containerWidth, height: containerHeight }),
    })
        .then(response => response.json())
        .then(data => {
            graphContainer.innerHTML = data.graph_div;

            // Execute any embedded Plotly scripts
            const scripts = graphContainer.getElementsByTagName('script');
            for (let i = 0; i < scripts.length; i++) {
                new Function(scripts[i].innerHTML)();
            }
        })
        .catch(error => {
            console.error('Error fetching match graph:', error);
            graphContainer.innerHTML = '<p>Error loading match graph</p>';
        });
}


