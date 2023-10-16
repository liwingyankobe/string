function LevelViewerRow({data}) {
    let levelPath;
    if (data[2] === 'None')
        levelPath = 'https://thestringharmony.com' + data[1];
    else
        levelPath = 'https://' + data[2].replace('/', ':') + '@thestringharmony.com' + data[1];

    return (
        <tr>
            <td>{data[0]}</td>
            <td>
                <a href={levelPath} target="_blank">{data[1]}</a>
            </td>
            <td>{data[2]}</td>
            <td>{data[3]}</td>
        </tr>
    )
}

export default LevelViewerRow;