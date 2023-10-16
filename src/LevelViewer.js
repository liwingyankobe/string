import { useState } from "react";
import LevelViewerRow from "./LevelViewerRow";

function LevelViewer({title, data}) {
    const [filter, setFilter] = useState(null);

    let processData = data;
    if (data.length > 0 && data[0].length === 5)
        for (let i = 0; i < data.length; i++) {
            processData[i][0] += ' ' + '⭐'.repeat(processData[i][4]);
            processData[i].pop();
        }

    let filterData = processData;
    if (filter !== null)
        filterData = processData.filter(row => row.some(entry => entry.toLowerCase().includes(filter.toLowerCase())));
    const filterRows = filterData.map(row => <LevelViewerRow key={row[0]} data={row}/>);

    function changeFilter(text) {
        setFilter(text === '' ? null : text);
    }

    return (
        <div>
            <h1>{title}</h1>
            <input
                type="text"
                value={filter === null ? '' : filter}
                onChange={e => {changeFilter(e.target.value)}}
                placeholder="Search"
                className="search"
            />
            {filterRows.length === 0 ?
                <p>No levels found.</p> : (
                <table>
                    <thead>
                        <tr>
                        <th>Level</th><th>Path</th><th>UN/PW</th><th>Solution</th>
                        </tr>
                    </thead>
                    <tbody>
                        {filterRows}
                    </tbody>
                </table>
            )}
        </div>
    );
}

export default LevelViewer;