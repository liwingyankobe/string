import { useState } from "react";
import AchievementEntry from "./AchievementEntry";

function AchievementViewer({userAc, ac}) {
    const [hover, setHover] = useState(null);

    let userAcSet = new Set();
    let acEntries = [];
    for (let i = 0; i < userAc.length; i++) {
        userAcSet.add(userAc[i][0]);
        acEntries.push(<AchievementEntry
            key={userAc[i][0]}
            found={true}
            hover={hover === userAc[i][0]}
            data={userAc[i]}
            onHover={() => setHover(userAc[i][0])}
            onLeave={() => setHover(null)}
        />);
    }

    for (let i = 0; i < ac.length; i++) {
        if (userAcSet.has(ac[i][0]))
            continue;
        acEntries.push(<AchievementEntry
            key={ac[i][0]}
            found={false}
            hover={hover === ac[i][0]}
            data={ac[i]}
            onHover={() => setHover(ac[i][0])}
            onLeave={() => setHover(null)}
        />);
    }

    return (
        <div className="achievements">
            <h1>Achievements</h1>
            {acEntries}
        </div>
    );
}

export default AchievementViewer;