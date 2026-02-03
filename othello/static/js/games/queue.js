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
});