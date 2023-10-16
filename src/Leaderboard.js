import { useState } from 'react';
import NavBar from './NavBar';
import LeaderboardRow from './LeaderboardRow';

function Leaderboard({data, secretInfo}) {
    const [page, setPage] = useState(1);
    const [hover, setHover] = useState(-1);

    const pageLimit = 25;
    const barLength = Math.ceil(data.length / pageLimit);
    const lowerLimit = pageLimit * (page - 1) + 1;
    const upperLimit = Math.min(pageLimit * page, data.length);

    let pageRows = [];
    for (let i = lowerLimit - 1; i < upperLimit; i++)
        pageRows.push(i === hover ?
            <LeaderboardRow
                key={'row' + i.toString()}
                data={data[i]}
                secretInfo={secretInfo}
                onHover={() => setHover(i)}
                onLeave={() => setHover(-1)}
            /> :
            <LeaderboardRow
                key={'row' + i.toString()}
                data={data[i]}
                onHover={() => setHover(i)}
                onLeave={() => setHover(-1)}
            />);

    return (
        <div>
            <h1>Leaderboard</h1>
            <table>
                <thead>
                    <tr>
                        <th>Rank</th><th>Nickname</th><th>Current Level</th><th>Bonus Score</th>
                    </tr>
                </thead>
                <tbody>
                    {pageRows}
                </tbody>
            </table>
            <NavBar barLength={barLength} currentPage={page} onSwitchPage={setPage}/>
        </div>
    );
}

export default Leaderboard;