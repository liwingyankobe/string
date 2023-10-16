window.onload = () => {
	const session = location.href.substring(location.href.indexOf('session')+8, location.href.length);
	if (location.href.indexOf("session") > -1) {
        document.cookie = 'string-session=' + session + ';Domain=.thestringharmony.com;Max-Age=31536000;Secure;Path=/';
		window.location.replace('https://thestringharmony.com/stringbot');
	} else {
		window.location.replace("https://discord.com/api/oauth2/authorize?client_id=859512367480963103&redirect_uri=http%3A%2F%2Fthe-string-harmony-bot.herokuapp.com%2Flogin&response_type=code&scope=identify")
	}
}