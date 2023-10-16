function LeaderboardRow({data, secretInfo = null, onHover, onLeave}) {
    let secret = null;
    if (secretInfo !== null && data[3][0] !== null) {
        secret = [];
        for (let i = 0; i < data[3].length; i++)
            secret.push(
                <span key={secretInfo[data[3][i] - 1][0]} style={{display: 'inline-block'}}>
                    <span className="dot" style={{backgroundColor: '#' + secretInfo[data[3][i] - 1][1]}}></span>
                    &nbsp;{secretInfo[data[3][i] - 1][0]}&nbsp;&nbsp;
                </span>
            );
    }

    return (
        <tr>
            <td>{data[0]}</td>
            <td>{data[1]}</td>
            <td>{data[2]}</td>
            <td>
                <div className="tooltipContainer">
                    <div onMouseOver={onHover} onMouseLeave={onLeave}>
                        {data[4]}
                    </div>
                    {secret !== null && (
                        <div className="tooltip">
                            {secret}
                        </div>
                    )}
                </div>
            </td>
        </tr>
    );
}

export default LeaderboardRow;