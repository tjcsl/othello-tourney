$(document).ready(function () {
    const ws_scheme = window.location.protocol === "https:" ? "wss" : "ws";
    const ws_path = ws_scheme + '://' + window.location.host + '/queue/';
    const socket = new WebSocket(ws_path);

    socket.onmessage = function (event) {
        const data = JSON.parse(event.data);
        if (data.type === 'match_update') {
            updateMatch(data);
        }
    };

    socket.onclose = function () {
        console.log('WebSocket closed');
    };

    function formatRatingDelta(delta) {
        const value = parseInt(delta);
        if (value > 0) return `+${value}`;
        if (value < 0) return value;
        return `±0`;
    }

    function ratingDeltaSpan(delta) {
        if (delta === null || delta === undefined) return '';

        const value = parseInt(delta);
        let cls = 'delta-tie';
        if (value > 0) cls = 'delta-win';
        else if (value < 0) cls = 'delta-loss';

        return `
            <span class="rating-delta ${cls}">
                (${formatRatingDelta(delta)})
            </span>
        `;
    }

    function resultCircle(result) {
        let cls = 'result-tie';
        if (result === 'W') cls = 'result-win';
        else if (result === 'L') cls = 'result-loss';

        return `<span class="result-circle ${cls}">${result}</span>`;
    }

    function buildScoreColumn(match) {
        if (match.status !== 'completed' || !match.score) {
            return `
                <span class="result-circle result-tie">-</span>
                <span class="score">? - ? - ?</span>
                <span class="result-circle result-tie">-</span>
            `;
        }

        const [p1Wins, ties, p2Wins] = match.score.split(' - ').map(Number);

        let p1Result = 'T';
        let p2Result = 'T';

        if (p1Wins > p2Wins) {
            p1Result = 'W';
            p2Result = 'L';
        } else if (p2Wins > p1Wins) {
            p1Result = 'L';
            p2Result = 'W';
        }

        return `
            ${resultCircle(p1Result)}
            <span class="score">${match.score}</span>
            ${resultCircle(p2Result)}
        `;
    }

    function updateMatch(data) {
        console.log("websocket update");

        const row = $(`.match[data-match-id="${data.match_id}"]`);
        if (!row.length) return;

        row.find('td:nth-child(1)').html(`
            ${data.player1}
            ${data.status === 'completed' ? ratingDeltaSpan(data.player1_rating_delta) : ''}
        `);

        row.find('td:nth-child(2)').html(buildScoreColumn({
            status: data.status,
            score: data.score
        }));

        row.find('td:nth-child(3)').html(`
            ${data.player2}
            ${data.status === 'completed' ? ratingDeltaSpan(data.player2_rating_delta) : ''}
        `);

        row.find('td:nth-child(4)').text(data.is_ranked);

        if (data.status === 'completed')
        row.find('td:nth-child(5)').html(
            `${data.status_display}${data.status === 'completed' ? ' <a href="/match_replay/' + data.match_id + '">(Replay)</a>' : ''}`
        );
    }

    $('#myMatchesCheckbox').change(function () {
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

        $.getJSON(url.toString(), function (data) {
            updateTable(data.matches);
        });
    }

    function updateTable(matches) {
        console.log("http update");
        const tbody = $('#matches');
        tbody.empty();

        matches.forEach(function (match) {
            const row = $(`
                <tr class="match" data-match-id="${match.id}">
                    <td class="align-middle">
                        ${match.player1_name}
                        ${match.status === 'completed' ? ratingDeltaSpan(match.player1_rating_delta) : ''}
                    </td>
                    <td class="align-middle score-column">
                        ${buildScoreColumn(match)}
                    </td>
                    <td class="align-middle">
                        ${match.player2_name}
                        ${match.status === 'completed' ? ratingDeltaSpan(match.player2_rating_delta) : ''}
                    </td>
                    <td class="align-middle">
                        ${match.is_ranked ? 'Yes' : 'No'}
                    </td>
                    <td class="align-middle">
                        ${match.status_display}${match.status === 'completed' ? ' <a href="/match_replay/' + match.id + '">(Replay)</a>' : ''}
                    </td>
                    <td class="align-middle">
                        ${match.created_at}
                    </td>
                </tr>
            `);

            tbody.append(row);
        });
    }

    setInterval(pollQueue, 10000);
});
