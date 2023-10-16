function NavBar({barLength, currentPage, onSwitchPage}) {
    let pageList = [];
    pageList.push(<button key='pageMin' className='unselected' onClick={() => onSwitchPage(1)}>«</button>);
    for (let i = 1; i <= barLength; i++)
        pageList.push(
                <button 
                    key={'page' + i.toString()}
                    className={currentPage === i ? 'selected' : 'unselected'}
                    onClick={() => onSwitchPage(i)}>
                    {i}
                </button>
        );
    pageList.push(<button key='pageMax' className='unselected' onClick={() => onSwitchPage(barLength)}>»</button>);

    return (
        <div className="navBar">
            {pageList}
        </div>
    );
}

export default NavBar;