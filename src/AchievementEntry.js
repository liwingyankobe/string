function AchievementEntry({found, hover, data, onHover, onLeave}) {
    const image = <img
        src={require('./cheevos/' + data[0] + '.jpg')}
        className={found ? 'unlockedImage' : 'lockedImage'}
        onMouseOver={onHover}
        onMouseLeave={onLeave}
    />;

    return (
        <div className="tooltipContainer imageContainer">
            {found ? (
                <a href={'https://thestringharmony.com' + data[2]} target="_blank">
                    {image}
                </a>
            ) : image}
            {hover && (
                <div className="tooltip">
                    <p><strong>{data[0]}</strong></p>
                    <p>{data[1]}</p>
                </div>
            )}
        </div>
    );
}

export default AchievementEntry;