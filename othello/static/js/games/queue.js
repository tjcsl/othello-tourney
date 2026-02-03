$(document).ready(function() {
    const ws_scheme = window.location.protocol === "https:" ? "wss" : "ws";
    const ws_path = ws_scheme + '://' + window.location.host + '/queue/';
    const socket = new WebSocket(ws_path);

    socket.onmessage = function(event) {
        const data = JSON.parse(event.data);
        if (data.type === 'match_update') {
            updateMatch(data);
        }
    };

    socket.onclose = function(event) {
        console.log('WebSocket closed');
    };

    function updateMatch(data) {
        console.log("websocket update");
        const matchRow = $(`.match[data-match-id="${data.match_id}"]`);

        let statusHtml = data.status;
        if (data.status === 'completed') {
            statusHtml += ` <a href="/match_replay/${data.match_id}/">(Replay)</a>`;
        }

        function applyWinLoseClasses(row) {
            row.find('td:nth-child(1), td:nth-child(3)')
                .removeClass('win lose');

            if (data.status !== 'completed') return;

            const parts = data.score.split('-').map(Number);
            if (parts.length !== 3) return;

            const p1Wins = parts[0];
            const p2Wins = parts[2];

            const p1Cell = row.find('td:nth-child(1)');
            const p2Cell = row.find('td:nth-child(3)');

            if (p1Wins > p2Wins) {
                p1Cell.addClass('win');
                p2Cell.addClass('lose');
            } else if (p2Wins > p1Wins) {
                p2Cell.addClass('win');
                p1Cell.addClass('lose');
            }
        }

        if (matchRow.length) {
            matchRow.find('td:nth-child(2)').text(data.score);
            matchRow.find('td:nth-child(5)').html(statusHtml);
            applyWinLoseClasses(matchRow);
        } else {
            const newRow = $(`
                <tr class="match" data-match-id="${data.match_id}">
                    <td>${data.player1}</td>
                    <td>${data.score}</td>
                    <td>${data.player2}</td>
                    <td>${data.ranked}</td>
                    <td>${statusHtml}</td>
                    <td>${data.created_at}</td>
                </tr>
            `);

            $('#matches').prepend(newRow);
            applyWinLoseClasses(newRow);
        }
    }

    $('#myMatchesCheckbox').change(function() {
        const url = new URL(window.location);
        if (this.checked) {
            url.searchParams.set('my_matches', '1');
        } else {
            url.searchParams.delete('my_matches');
        }
        window.location.href = url.toString();
    });

    function pollQueue() {
        const url = new URL(window.location);

        url.pathname = url.pathname.replace('/queue/', '/queue/json/');

        if (!url.searchParams.has('page')) {
            url.searchParams.set('page', '1');
        }

        $.getJSON(url.toString(), function(data) {
            updateTable(data.matches);
        });
    }


    function updateTable(matches) {
        console.log("http update");
        const tbody = $('#matches');
        tbody.empty();

        matches.forEach(function(match) {
            let statusHtml = match.status;
            if (match.status === 'completed' && match.can_view_replay) {
                statusHtml += ` <a href="/match_replay/${match.id}/">(Replay)</a>`;
            }

            const row = $(`
                <tr class="match" data-match-id="${match.id}">
                    <td>${match.player1_name}</td>
                    <td>${match.score}</td>
                    <td>${match.player2_name}</td>
                    <td>${match.is_ranked}</td>
                    <td>${statusHtml}</td>
                    <td>${match.created_at}</td>
                </tr>
            `);

            row.find('td:nth-child(1), td:nth-child(3)')
                .removeClass('win lose');

            if (match.status === 'completed' && match.score) {
                const parts = match.score.split('-').map(Number);

                if (parts.length === 3) {
                    const p1Wins = parts[0];
                    const p2Wins = parts[2];

                    const p1Cell = row.find('td:nth-child(1)');
                    const p2Cell = row.find('td:nth-child(3)');

                    if (p1Wins > p2Wins) {
                        p1Cell.addClass('win');
                        p2Cell.addClass('lose');
                    } else if (p2Wins > p1Wins) {
                        p2Cell.addClass('win');
                        p1Cell.addClass('lose');
                    }
                }
            }

            tbody.append(row);
        });
    }


    setInterval(pollQueue, 10000);
});
