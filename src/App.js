import { useState } from 'react';
import Menu from './Menu';
import Leaderboard from './Leaderboard';
import LevelViewer from './LevelViewer';
import AchievementViewer from './AchievementViewer';

function readCookie(name) {
	var nameEQ = name + "=";
	var ca = document.cookie.split(';');
	for(var i=0;i < ca.length;i++) {
		var c = ca[i];
		while (c.charAt(0)==' ') c = c.substring(1,c.length);
		if (c.indexOf(nameEQ) == 0) return c.substring(nameEQ.length,c.length);
	}
	return null;
}

let userData = null;
const apiURL = 'https://the-string-harmony-bot.herokuapp.com/';
const sessionId = readCookie('string-session');
if (sessionId !== null) {
  const retrieveURL = apiURL + 'retrieve';
  const sessionData = {session: sessionId};
  const retrieveResponse = await fetch(retrieveURL, {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json',
    },
    body: JSON.stringify(sessionData)
  });
  userData = retrieveResponse.ok ? await retrieveResponse.json() : null;
}
if (userData === null || localStorage.getItem('tab') === null)
  localStorage.setItem('tab', 'Leaderboard');

const leaderboardURL = apiURL + 'leaderboard';
const leaderboardResponse = await fetch(leaderboardURL);
const leaderboardData = await leaderboardResponse.json();

const secretInfoURL = apiURL + 'secret_info';
const secretInfoResponse = await fetch(secretInfoURL);
const secretInfo = await secretInfoResponse.json();

const achievementInfoURL = apiURL + 'achievement_info';
const achievementInfoResponse = await fetch(achievementInfoURL);
const achievementInfo = await achievementInfoResponse.json();

function App() {
  const [tab, setTab] = useState(localStorage.getItem('tab'));

  function switchTab(tab) {
    localStorage.setItem('tab', tab);
    setTab(tab);
  }

  return (
    <div>
      <header className='header'>
        {userData !== null ?
          <Menu
            items={['Leaderboard', 'Main Levels', 'Optional Levels', 'Achievements']}
            nickname={userData.nickname}
            onTabChange={switchTab}
          /> :
          <Menu
            items={['Leaderboard']}
            nickname={null}
            onTabChange={switchTab}
          />
        }
      </header>

      {tab === 'Leaderboard' ?
        <Leaderboard data={leaderboardData} secretInfo={secretInfo}/> : 
      tab === 'Main Levels' ?
        <LevelViewer title="Main Levels" data={userData.mains}/> : 
      tab === 'Optional Levels' ?
        <LevelViewer title="Optional Levels" data={userData.secrets}/> :
      tab === 'Achievements' ?
        <AchievementViewer userAc={userData.achievements} ac={achievementInfo}/> : null
      }
    </div>
  );
}

export default App;
