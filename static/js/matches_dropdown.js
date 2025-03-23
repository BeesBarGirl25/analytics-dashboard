const matchCache = {}; // Client-side cache for match data

document.addEventListener('DOMContentLoaded', function () {
    document.addEventListener('DropdownPopulated', function (event) {
        const { competition_id, season_id } = event.detail;
        console.log(`Received Competition ID: ${competition_id}, Season ID: ${season_id}`);
        populateMatchesDropdown(competition_id, season_id);
    });

    document.addEventListener('MatchDropdownPopulated', function (event) {
        const { match_id } = event.detail;
        console.log(`Received Match ID: ${match_id}`);

        // Fetch match data and pass it to other functions
        getMatchData(match_id)
            .then(data => {
                console.log("Match data received:", data);

                // Example: Use match data for graph generation
                getMatchGraph(match_id);
            })
            .catch(error => {
                console.error("Error fetching match data:", error);
            });
    });
});


function populateMatchesDropdown(competition_id, season_id) {
    // Fetch matches from the backend
    fetch('/fetch_matches', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ competition_id, season_id }),
})
    .then(response => response.json())
    .then(data => {
        const matchDropdown = document.getElementById('matchDropdown');
        const selectedItemMatches = document.getElementById('selectedItemMatches');
        matchDropdown.innerHTML = ''; // Clear existing options

        const groupedData = data.reduce((groups, item) => {
            const { competition_stage, value, text } = item;
            if (!groups[competition_stage]) {
                groups[competition_stage] = [];
            }
            groups[competition_stage].push({ value, text });
            return groups;
        }, {});

        Object.entries(groupedData).forEach(([competitionStage, matches]) => {
            const competitionStageDiv = document.createElement('div');
            competitionStageDiv.className = 'stage';
            competitionStageDiv.textContent = competitionStage;

            const matchesList = document.createElement('div');
            matchesList.className = 'matches-list';

            matches.forEach(({ value, text }) => {
                const matchDiv = document.createElement('div');
                matchDiv.className = 'match';
                matchDiv.textContent = text;
                matchDiv.dataset.value = value; // Use `dataset` for custom attributes

                matchDiv.addEventListener('click', function () {
                    selectedItemMatches.textContent = text;
                    matchDropdown.style.display = 'none'; // Collapse dropdown
                    console.log(`Selected: Match ID ${value}`);
                    const event = new CustomEvent('MatchDropdownPopulated', {
                        detail: { match_id: value },
                    });
                    document.dispatchEvent(event);
                });

                matchesList.appendChild(matchDiv);
            });

            competitionStageDiv.addEventListener('click', function () {
                const isVisible = matchesList.style.display === 'block';
                matchesList.style.display = isVisible ? 'none' : 'block';
            });

            matchDropdown.appendChild(competitionStageDiv);
            matchDropdown.appendChild(matchesList);
        });

        selectedItemMatches.addEventListener('click', function () {
            const isVisible = matchDropdown.style.display === 'block';
            matchDropdown.style.display = isVisible ? 'none' : 'block';
        });
    })
    .catch(error => {
        console.error('Error fetching matches:', error);
    });
}

function getMatchData(match_id) {
    return new Promise((resolve, reject) => {
        // Check cache first
        if (matchCache[match_id]) {
            console.log("Using cached match data:", matchCache[match_id]);
            resolve(matchCache[match_id]);
            return;
        }

        // Fetch from /fetch_match endpoint
        fetch('/fetch_match', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ match_id }),
        })
            .then(response => {
                if (!response.ok) throw new Error(`HTTP error! Status: ${response.status}`);
                return response.json();
            })
            .then(data => {
                matchCache[match_id] = data; // Cache data
                resolve(data);
            })
            .catch(reject);
    });
}

function getMatchGraph(match_id) {
    const graphContainer = document.getElementById('match-graph-container');
    const containerWidth = graphContainer.clientWidth;
    const containerHeight = graphContainer.clientHeight;

    fetch('/fetch_match_graph', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ match_id, width: containerWidth, height: containerHeight }),
    })
        .then(response => response.json())
        .then(data => {
            graphContainer.innerHTML = data.graph_div;

            const scripts = graphContainer.getElementsByTagName('script');
            for (let i = 0; i < scripts.length; i++) {
                new Function(scripts[i].innerHTML)();
            }
        })
        .catch(error => {
            console.error("Error fetching match graph:", error);
            graphContainer.innerHTML = '<p>Error loading match graph</p>';
        });
}



