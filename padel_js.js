   
        // Game variables
        let score_1 = 0;
        let score_2 = 0;
        let games_1 = 0;
        let games_2 = 0;
        let sets_1 = 0;
        let sets_2 = 0;
        let time = "19H22";
        let lastAction = null;
        let matchWon = false;
        let winnerData = null;

        // LOCAL: Simple storage for sets history only
        let totalPointsBlack = 0;
        let totalPointsYellow = 0;
        let totalGamesBlack = 0;
        let totalGamesYellow = 0;
        let matchStartTime = Date.now();
        let setsHistory = []; // Only track sets, not individual points/games

        // API base URL
        const API_BASE = "http://localhost:5000";

        // Enhanced logo setup
        function setupLogo() {
            const logo = document.getElementById('logoClick');
            const logoImg = document.getElementById('logoImg');

            logoImg.onload = function() {
                console.log('✅ Logo image loaded');
                logo.classList.remove('no-image');
            };

            logoImg.onerror = function() {
                console.log('⚠️ Logo image failed, using fallback');
                logo.classList.add('no-image');
            };

            if (logoImg.complete) {
                if (logoImg.naturalWidth === 0) {
                    logoImg.onerror();
                } else {
                    logoImg.onload();
                }
            }
        }

        // LOCAL: Calculate match duration
        function getMatchDuration() {
            const durationMs = Date.now() - matchStartTime;
            const durationSeconds = Math.floor(durationMs / 1000);
            const minutes = Math.floor(durationSeconds / 60);
            const seconds = durationSeconds % 60;

            return minutes > 0 ? `${minutes}m ${seconds}s` : `${seconds}s`;
        }

        // SIMPLIFIED: Populate ONLY Sets Table
        function populateSetsTable() {
            const setsTableBody = document.getElementById('setsTableBody');

            if (setsHistory.length === 0) {
                setsTableBody.innerHTML = '<tr><td colspan="4" style="text-align:center; color:#ccc; font-style:italic;">No sets completed yet</td></tr>';
                return;
            }

            setsTableBody.innerHTML = setsHistory.map((set, index) => {
                const setNumber = index + 1;
                const winner = set.blackGames > set.yellowGames ? 'BLACK' : 'YELLOW';
                const winnerClass = set.blackGames > set.yellowGames ? 'winner-set' : '';

                return `
                    <tr>
                        <td><strong>Set ${setNumber}</strong></td>
                        <td class="${set.blackGames > set.yellowGames ? 'winner-set' : ''}">${set.blackGames}</td>
                        <td class="${set.yellowGames > set.blackGames ? 'winner-set' : ''}">${set.yellowGames}</td>
                        <td class="team-column ${winner.toLowerCase()}">${winner}</td>
                    </tr>
                `;
            }).join('');

            // Add current set if in progress
            if (games_1 > 0 || games_2 > 0) {
                const currentSetRow = `
                    <tr style="opacity: 0.7; font-style: italic;">
                        <td><strong>Set ${setsHistory.length + 1}</strong></td>
                        <td>${games_1}</td>
                        <td>${games_2}</td>
                        <td style="color: #ccc;">In Progress</td>
                    </tr>
                `;
                setsTableBody.innerHTML += currentSetRow;
            }
        }

        // Fetch game state from backend
        async function fetchGameState() {
            try {
                const response = await fetch(`${API_BASE}/game_state`);
                const data = await response.json();

                score_1 = data.score_1;
                score_2 = data.score_2;
                games_1 = data.game_1;
                games_2 = data.game_2;
                sets_1 = data.set_1 || 0;
                sets_2 = data.set_2 || 0;
                matchWon = data.match_won || false;
                winnerData = data.winner || null;

                updateScoreboard();

                if (matchWon && winnerData) {
                    showSetsWinner(winnerData);
                }

                console.log('Game state synced');
            } catch (error) {
                console.log('Running in offline mode');
            }
        }

        // Update scoreboard display
        function updateScoreboard() {
            document.getElementById('score1').textContent = score_1;
            document.getElementById('score2').textContent = score_2;
            document.getElementById('games1').textContent = games_1;
            document.getElementById('games2').textContent = games_2;
            document.getElementById('sets1').textContent = sets_1;
            document.getElementById('sets2').textContent = sets_2;
            document.getElementById('timeDisplay').textContent = time;
        }

        // Show click feedback
        function showClickFeedback(team) {
            if (matchWon) return;

            const teamElement = document.querySelector(`.${team}-team`);
            const feedback = document.createElement('div');
            feedback.className = 'click-feedback';
            feedback.textContent = '+1';
            teamElement.appendChild(feedback);

            setTimeout(() => {
                if (teamElement.contains(feedback)) {
                    teamElement.removeChild(feedback);
                }
            }, 800);
        }

        // SIMPLIFIED: Show winner with ONLY sets table
        function showSetsWinner(winner) {
            const winnerDisplay = document.getElementById('winnerDisplay');
            const winnerTeamName = document.getElementById('winnerTeamName');
            const finalScoreValue = document.getElementById('finalScoreValue');
            const durationValue = document.getElementById('durationValue');
            const totalPointsValue = document.getElementById('totalPointsValue');

            // Populate winner information
            winnerTeamName.textContent = winner.team_name;
            finalScoreValue.textContent = `${sets_1}-${sets_2}`;
            durationValue.textContent = getMatchDuration();
            totalPointsValue.textContent = `${totalPointsBlack}-${totalPointsYellow}`;

            // Populate ONLY sets table
            populateSetsTable();

            winnerDisplay.style.display = 'flex';
            matchWon = true;

            console.log('🏆 Winner display with ONLY sets history shown');
        }

        // Close winner and reset
        function closeWinner() {
            document.getElementById('winnerDisplay').style.display = 'none';
            resetMatch();
        }

        // Share result
        function shareResult() {
            const duration = getMatchDuration();
            const points = `${totalPointsBlack}-${totalPointsYellow}`;

            let shareText = '';
            if (winnerData) {
                shareText = `🏆 ${winnerData.team_name} wins!\n` +
                           `Final: ${sets_1}-${sets_2}\n` +
                           `Duration: ${duration}\n` +
                           `Points: ${points}`;
            } else {
                shareText = '🏆 Great padel match completed!';
            }

            if (navigator.share) {
                navigator.share({
                    title: 'Padel Match Result',
                    text: shareText,
                    url: window.location.href
                });
            } else if (navigator.clipboard) {
                navigator.clipboard.writeText(shareText);
                alert('Match result copied to clipboard!');
            } else {
                alert(shareText);
            }
        }

        // Show history popup (simplified sets only)
        function showHistory() {
            if (setsHistory.length === 0) {
                alert('No sets history available yet!');
                return;
            }

            const historyWindow = window.open('', '_blank', 'width=600,height=500');
            historyWindow.document.write(`
                <html>
                <head><title>Sets History</title>
                <style>
                    body { font-family: Arial, sans-serif; padding: 30px; background: #f5f5f5; }
                    .header { background: linear-gradient(135deg, #d4af37, #b8860b); padding: 20px; margin-bottom: 30px; border-radius: 10px; color: #000; }
                    .sets-table { width: 100%; border-collapse: collapse; background: white; border-radius: 8px; overflow: hidden; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
                    .sets-table th { background: #d4af37; color: #000; padding: 15px; text-align: center; }
                    .sets-table td { padding: 12px; text-align: center; border-bottom: 1px solid #eee; }
                    .sets-table tr:hover { background: #f9f9f9; }
                    .winner-cell { background: #fff2cc; font-weight: bold; }
                </style>
                </head>
                <body>
                <div class="header">
                    <h1>🏆 Sets History</h1>
                    ${winnerData ? `<h2>Winner: ${winnerData.team_name}</h2>` : ''}
                    <p>Match Duration: ${getMatchDuration()}</p>
                </div>
                <table class="sets-table">
                    <thead>
                        <tr><th>Set</th><th>Black Team</th><th>Yellow Team</th><th>Winner</th></tr>
                    </thead>
                    <tbody>
                        ${setsHistory.map((set, index) => `
                            <tr>
                                <td><strong>Set ${index + 1}</strong></td>
                                <td class="${set.blackGames > set.yellowGames ? 'winner-cell' : ''}">${set.blackGames}</td>
                                <td class="${set.yellowGames > set.blackGames ? 'winner-cell' : ''}">${set.yellowGames}</td>
                                <td class="winner-cell">${set.blackGames > set.yellowGames ? 'BLACK TEAM' : 'YELLOW TEAM'}</td>
                            </tr>
                        `).join('')}
                        ${games_1 > 0 || games_2 > 0 ? `
                            <tr style="opacity: 0.7; font-style: italic;">
                                <td><strong>Set ${setsHistory.length + 1}</strong></td>
                                <td>${games_1}</td>
                                <td>${games_2}</td>
                                <td>In Progress</td>
                            </tr>
                        ` : ''}
                    </tbody>
                </table>
                </body>
                </html>
            `);
        }

        // Send point to backend
        async function sendPointToBackend(team) {
            try {
                const response = await fetch(`${API_BASE}/add_point`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ team: team })
                });

                if (response.ok) {
                    const data = await response.json();
                    if (data.match_won) {
                        showSetsWinner(data.winner);
                    }
                    return true;
                }
            } catch (error) {
                console.log('Backend unavailable, using local mode');
                return false;
            }
        }

        // Add point with simplified tracking
        async function addPoint(team) {
            if (matchWon) { 
                return;
            }

            showClickFeedback(team);

            // Store last action for undo
            lastAction = {
                team: team,
                prevScore1: score_1,
                prevScore2: score_2,
                prevGames1: games_1,
                prevGames2: games_2,
                prevSets1: sets_1,
                prevSets2: sets_2,
                prevTotalPointsBlack: totalPointsBlack,
                prevTotalPointsYellow: totalPointsYellow,
                prevTotalGamesBlack: totalGamesBlack,
                prevTotalGamesYellow: totalGamesYellow,
                prevSetsHistoryLength: setsHistory.length
            };

            // Update local point counters
            if (team === 'black') {
                totalPointsBlack++;
            } else {
                totalPointsYellow++;
            }

            // Try backend first
            const backendSuccess = await sendPointToBackend(team);

            if (backendSuccess) {
                await fetchGameState();
            } else {
                // Local logic
                if (team === 'black') {
                    score_1 = nextTennisScore(score_1);
                    if (score_1 === 0) {
                        games_1++;
                        totalGamesBlack++;
                        score_2 = 0;
                        checkSetWin('black');
                    }
                } else if (team === 'yellow') {
                    score_2 = nextTennisScore(score_2);
                    if (score_2 === 0) {
                        games_2++;
                        totalGamesYellow++;
                        score_1 = 0;
                        checkSetWin('yellow');
                    }
                }
                updateScoreboard();
            }
        }

        // Check set win with simplified history tracking
        function checkSetWin(team) {
            if (team === 'black' && games_1 >= 6 && games_1 - games_2 >= 2) {
                // Store set result
                setsHistory.push({
                    blackGames: games_1,
                    yellowGames: games_2,
                    winner: 'black'
                });

                sets_1++;
                games_1 = 0;
                games_2 = 0;
                checkMatchWin('black');
            } else if (team === 'yellow' && games_2 >= 6 && games_2 - games_1 >= 2) {
                // Store set result
                setsHistory.push({
                    blackGames: games_1,
                    yellowGames: games_2,
                    winner: 'yellow'
                });

                sets_2++;
                games_1 = 0;
                games_2 = 0;
                checkMatchWin('yellow');
            }
        }

        // Check match win
        function checkMatchWin(team) {
            if ((team === 'black' && sets_1 >= 2) || (team === 'yellow' && sets_2 >= 2)) {
                const winner = {
                    team_name: team === 'black' ? 'BLACK TEAM' : 'YELLOW TEAM',
                    final_sets: `${sets_1}-${sets_2}`,
                    match_summary: 'Match completed'
                };
                winnerData = winner;
                showSetsWinner(winner);
            }
        }

        // Tennis scoring logic
        function nextTennisScore(current) {
            switch(current) {
                case 0: return 15;
                case 15: return 30;
                case 30: return 40;
                case 40: return 0;
                default: return 0;
            }
        }

        // Reset match
        async function resetMatch() {
            if (confirm('Reset the entire match?')) {
                try {
                    const response = await fetch(`${API_BASE}/reset_match`, {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' }
                    });

                    if (response.ok) {
                        await fetchGameState();
                    }
                } catch (error) {
                    // Local reset
                    score_1 = 0;
                    score_2 = 0;
                    games_1 = 0;
                    games_2 = 0;
                    sets_1 = 0;
                    sets_2 = 0;
                    matchWon = false;
                    winnerData = null;
                    updateScoreboard();
                }

                // Clear local data
                totalPointsBlack = 0;
                totalPointsYellow = 0;
                totalGamesBlack = 0;
                totalGamesYellow = 0;
                setsHistory = [];
                matchStartTime = Date.now();

                document.getElementById('winnerDisplay').style.display = 'none';
                console.log('🔄 Match reset with sets history cleared');
            }
        }

        // Undo last point
        function undoLastPoint() {
            if (matchWon) {
                alert('Cannot undo after match is finished!');
                return;
            }

            if (lastAction) {
                score_1 = lastAction.prevScore1;
                score_2 = lastAction.prevScore2;
                games_1 = lastAction.prevGames1;
                games_2 = lastAction.prevGames2;
                sets_1 = lastAction.prevSets1;
                sets_2 = lastAction.prevSets2;

                totalPointsBlack = lastAction.prevTotalPointsBlack;
                totalPointsYellow = lastAction.prevTotalPointsYellow;
                totalGamesBlack = lastAction.prevTotalGamesBlack;
                totalGamesYellow = lastAction.prevTotalGamesYellow;

                setsHistory = setsHistory.slice(0, lastAction.prevSetsHistoryLength);

                updateScoreboard();
                lastAction = null;
                console.log('Last action undone');
            }
        }

        // Enhanced logo click
        document.getElementById('logoClick').addEventListener('click', function() {
            this.style.transform = 'scale(0.9) rotate(360deg)';
            setTimeout(() => {
                this.style.transform = 'scale(1) rotate(0deg)';
            }, 400);
        });

        // Initialize
        document.addEventListener('DOMContentLoaded', function() {
            setupLogo();
            fetchGameState();
            updateScoreboard();
            matchStartTime = Date.now();
        });

        // Auto-update time
        setInterval(() => {
            const now = new Date();
            const hours = String(now.getHours()).padStart(2, '0');
            const minutes = String(now.getMinutes()).padStart(2, '0');
            time = `${hours}H${minutes}`;
            updateScoreboard();
        }, 60000);

        // Keyboard shortcuts
        document.addEventListener('keydown', function(e) {
            if (matchWon) return;

            switch(e.key) {
                case 'ArrowLeft':
                case 'a':
                case 'A':
                    addPoint('black');
                    break;
                case 'ArrowRight':
                case 'd':
                case 'D':
                    addPoint('yellow');
                    break;
                case 'r':
                case 'R':
                    resetMatch();
                    break;
                case 'u':
                case 'U':
                    undoLastPoint();
                    break;
                case 's':
                case 'S':
                    fetchGameState();
                    break;
                case 'h':
                case 'H':
                    showHistory();
                    break;
            }
        });
    