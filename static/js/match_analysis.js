const matchCache = {}; // Client-side cache for match data
const matchesCache = {};

document.addEventListener('DOMContentLoaded', function () {
    document.addEventListener('DropdownPopulated', function (event) {
        const { competition_id, season_id } = event.detail;
        populateMatchesDropdown(competition_id, season_id);
    });

    document.addEventListener('MatchDropdownPopulated', function (event) {
    const { match_id } = event.detail;

    getMatchData(match_id)
        .then(data => {
            // Dynamically update tab labels
            const uniqueTeams = [...new Set(data.map(item => item.team))];
            if (uniqueTeams.length === 2) {
                document.querySelector('.tab-button:nth-child(2)').textContent = uniqueTeams[0];
                document.querySelector('.tab-button:nth-child(3)').textContent = uniqueTeams[1];
            }

            if (uniqueTeams.length === 2) {
                loadSquadForTab(uniqueTeams[0], match_id, "team1-table-container");
                loadSquadForTab(uniqueTeams[1], match_id, "team2-table-container");
            }

            // Cache match data
            matchCache[match_id] = data;
            getMatchGraph(match_id);
            loadMatchOverview(match_id);
            // Render content for the currently active tab
            const activeTab = document.querySelector('.tab-button.active');
            if (activeTab) {
                const tabId = activeTab.getAttribute('onclick').match(/showTab\('(.*?)'\)/)[1];
                const teamName = activeTab.textContent;

                // Call the squad table rendering logic for the active tab
                if (tabId === "team1Tab" || tabId === "team2Tab") {
                    loadSquadForTab(
                        teamName,
                        match_id,
                        tabId === "team1Tab" ? "team1-table-container" : "team2-table-container"
                    );
                }
            }
        })
        .catch(error => console.error("Error fetching match data:", error));

});

});

function populateMatchesDropdown(competition_id, season_id) {
    const matchDropdown = document.getElementById('matchDropdown'); // Matches dropdown container
    const selectedItemMatches = document.getElementById('selectedItemMatches'); // Matches dropdown toggle button
    const graphContainer = document.getElementById('match-graph-container'); // Graph container

    // Clear previous matches and graph content
    matchDropdown.innerHTML = '<div class="loading">Loading matches...</div>'; // Add a loading message
    selectedItemMatches.textContent = 'Select a Match'; // Reset the selected match display
    graphContainer.innerHTML = '<p>Please select a match to view its graph.</p>'; // Reset the graph container

    // Ensure dropdown visibility toggle listener is attached properly
    selectedItemMatches.onclick = function () {
        const isVisible = matchDropdown.style.display === 'block';
        matchDropdown.style.display = isVisible ? 'none' : 'block';
    };

    // Fetch matches from the backend
    fetch('/fetch_matches', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ competition_id, season_id }),
    })
    .then(response => response.json())
    .then(data => {
        console.log("Comp data: ", competition_id, season_id)
        // Clear the loading message
        matchDropdown.innerHTML = '';

        data.forEach(match => {
            const {match_id, ...matchData } = match;
            matchesCache[match_id] = matchData;
        })

        console.log('Matches Cache: ', matchesCache)

        parsedData = data.map(row => ({
            competitionStage: row.competition_stage,
            value: row.match_id,
            text: `${row.home_team} vs ${row.away_team}`
        }))



        // Organize data by competition stages
        const groupedData = parsedData.reduce((groups, item) => {
            const { competitionStage, value, text } = item;
            if (!groups[competitionStage]) {
                groups[competitionStage] = [];
            }
            groups[competitionStage].push({ value, text });
            return groups;
        }, {});


        console.log('groupedData: ', groupedData)
        // Populate the matches dropdown
        Object.entries(groupedData).forEach(([competitionStage, matches]) => {
            // Create a stage header
            const competitionStageDiv = document.createElement('div');
            competitionStageDiv.className = 'stage';
            competitionStageDiv.textContent = competitionStage;

            // Create a list of matches under this stage
            const matchesList = document.createElement('div');
            matchesList.className = 'matches-list';

            matches.forEach(({ value, text }) => {
                const matchDiv = document.createElement('div');
                matchDiv.className = 'match';
                matchDiv.textContent = text;
                matchDiv.dataset.value = value;

                // Attach the event listener to dynamically handle match selection
                matchDiv.onclick = function () {
                    selectedItemMatches.textContent = text; // Update the selected match display
                    matchDropdown.style.display = 'none'; // Collapse the dropdown

                    // Dispatch a custom event for the selected match
                    const event = new CustomEvent('MatchDropdownPopulated', {
                        detail: { match_id: value },
                    });
                    document.dispatchEvent(event);
                };

                matchesList.appendChild(matchDiv);
            });

            // Add a toggle to show/hide the matches under this stage
            competitionStageDiv.onclick = function () {
                const isVisible = matchesList.style.display === 'block';
                matchesList.style.display = isVisible ? 'none' : 'block';
            };

            // Append the stage and matches to the dropdown
            matchDropdown.appendChild(competitionStageDiv);
            matchDropdown.appendChild(matchesList);
        });

    })
    .catch(error => {
        console.error('Error fetching matches:', error);
        matchDropdown.innerHTML = '<div class="error">Error loading matches. Please try again.</div>'; // Show error message
    });
}

function getMatchData(match_id) {
    return new Promise((resolve, reject) => {
        // Check cache first
        if (matchCache[match_id]) {
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

function showTab(tabId) {
    const tabs = document.querySelectorAll('.tab-content');
    tabs.forEach(tab => tab.classList.remove('active'));

    const buttons = document.querySelectorAll('.tab-button');
    buttons.forEach(button => button.classList.remove('active'));

    document.getElementById(tabId).classList.add('active');
    event.target.classList.add('active');

    const matchId = getCurrentMatchId(); // Retrieve the current match ID

    if (tabId === "team1Tab" || tabId === "team2Tab") {
        const teamName = document.querySelector(
            tabId === "team1Tab" ? '.tab-button:nth-child(2)' : '.tab-button:nth-child(3)'
        ).textContent;

        loadSquadForTab(
            teamName,
            matchId,
            tabId === "team1Tab" ? "team1-table-container" : "team2-table-container"
        );
    }
}

function filterMatchDataByTeam(teamName, matchId) {
    const matchData = matchCache[matchId]; // Retrieve the cached match data

    if (!matchData) {
        console.error("Match data not found in cache.");
        return [];
    }

    // Filter match data by the specified team name
    return matchData.filter(item => item.team === teamName);
}

function createDynamicTableHTML(data) {
    if (data.length === 0) {
        return '<p>No data available.</p>';
    }

    const columns = Object.keys(data[0]);
    let tableHTML = '<table class="squad-table"><thead><tr>';

    // Create header row
    columns.forEach(column => {
        tableHTML += `<th>${column}</th>`;
    });

    tableHTML += '</tr></thead><tbody>';

    // Create data rows
    data.forEach(row => {
        tableHTML += '<tr>';
        columns.forEach(column => {
            const cellData = row[column] || "No Data"; // Replace NaN or empty values
            tableHTML += `<td>${cellData}</td>`;
        });
        tableHTML += '</tr>';
    });

    tableHTML += '</tbody></table>';
    return tableHTML;
}

function loadSquadForTab(teamName, matchId, containerId) {
    const container = document.getElementById(containerId);
    container.innerHTML = '<p>Loading...</p>'; // Display a loading message

    fetch('/fetch_team_squad', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ match_id: matchId, team_name: teamName })
    })
        .then(response => response.json())
        .then(data => {
            container.innerHTML = data.html; // Populate the table with the returned HTML
        })
        .catch(error => {
            console.error("Error loading squad data:", error);
            container.innerHTML = '<p>Error loading data.</p>';
        });
}

function loadMatchOverview(matchId) {

    const matchFetch = fetch('/fetch_match', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ match_id: matchId })
    });

    const matchOverviewFetch = fetch('/fetch_match_overview', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ match_id: matchId })
    });

    // Wait for both fetches to resolve
    Promise.all([matchFetch, matchOverviewFetch])
        .then(async ([matchResponse, overviewResponse]) => {
            const matchData = await matchResponse.json();
            const overviewData = await overviewResponse.json();

            console.log(overviewData)
            document.querySelector('.homeTeamName').textContent = overviewData.home_team
            document.querySelector('.awayTeamName').textContent = overviewData.away_team
            document.querySelector('.matchScore').textContent = overviewData.home_score + ' - ' + overviewData.away_score
            document.querySelector('.homeTeam .scorers').textContent = overviewData.home_goals
            document.querySelector('.awayTeam .scorers').textContent = overviewData.away_goals
            document.querySelector('.homeTeam .assists').textContent = overviewData.home_assists
            document.querySelector('.awayTeam .assists').textContent = overviewData.away_assists
            document.querySelector('.homeTeam .manager').textContent = overviewData.home_managers
            document.querySelector('.awayTeam .manager').textContent = overviewData.away_managers
            document.querySelector('.referee').textContent = 'Referee: ' + overviewData.referee
            document.querySelector('#homeTeamShots').textContent = overviewData.home_shots
            document.querySelector('#awayTeamShots').textContent = overviewData.away_shots
            document.querySelector('#homeTeamPassesAttempted').textContent = overviewData.home_passes
            document.querySelector('#awayTeamPassesAttempted').textContent = overviewData.away_passes
            document.querySelector('#homeTeamPassesCompleted').textContent = overviewData.home_passes_complete
            document.querySelector('#awayTeamPassesCompleted').textContent = overviewData.away_passes_complete
         })
        .catch(error => {
            console.error("Error loading match data:", error);
        });
}








