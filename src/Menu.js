function Menu({items, nickname, onTabChange}) {
    function login() {
        window.location.replace("https://thestringharmony.com/login");
    }

    function logout() {
        document.cookie = 'string-session=;Domain=.thestringharmony.com;Max-Age=-99999999;Path=/';
        window.location.reload();
    }

    let buttonList = items.map(item => <button key={item} className='menuButton' onClick={() => onTabChange(item)}>{item}</button>);
    if (nickname === null)
        buttonList.push(<button key='Login' className='menuButton' onClick={login}>Login</button>);
    else
        buttonList.push(<button key='Logout' className='menuButton' onClick={logout}>Logout</button>);
    return (
        <div className="menu">
            <div className="leftMenu">
                {buttonList}
            </div>
            <div className="rightMenu">
                <button className="menuText">{nickname !== null ? 'Welcome, ' + nickname : ''}</button>
            </div>
        </div>
    );
}

export default Menu;