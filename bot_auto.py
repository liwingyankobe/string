import discord
import os
import requests
import asyncio
import psycopg2, psycopg2.extras
import random
from discord.ext import commands
from quart import Quart, request, make_response, redirect

TOKEN = ''
DATABASE_URL = os.environ['DATABASE_URL']
connection = psycopg2.connect(DATABASE_URL, sslmode='require')
cursor = connection.cursor()

intents = discord.Intents.all()
bot = commands.Bot(command_prefix='!', intents=intents)
app = Quart(__name__)

level_names = []
level_paths = []
level_solutions = []
max_namelen = 32
cursor.execute('select name, path, solution from mains order by id')
data = cursor.fetchall()
for d in data:
    level_names.append(d[0])
    max_namelen = min(max_namelen, 29 - len(d[0]))
    level_paths.append(d[1])
    level_solutions.append(d[2])
level_count = len(level_names) - 1
medal = level_names[-1]

unpw_id = []
unpw_answers = []
cursor.execute('select * from unpw order by id')
data = cursor.fetchall()
for d in data:
    unpw_id.append(d[0] - 1)
    unpw_answers.append(d[1])

mile_id = []
mile_role = []
cursor.execute('select * from milestones order by id')
data = cursor.fetchall()
for d in data:
    mile_id.append(d[0] - 1)
    mile_role.append(d[1])

role_list = []
for i in range(1,level_count):
    role_list.append('reached-' + level_names[i])
role_list.append(mile_role[-1])

secret_names = []
secret_identifiers = []
secret_level_paths = []
secret_solution_paths = []
secret_solutions = []
secret_unpw = []
secret_rating = []
secret_reach = []
cursor.execute('select name, level_path, solution_path, solution, unpw, rating, reach_role, reach_replace from secrets order by id')
data = cursor.fetchall()
for d in data:
    secret_names.append(d[0])
    secret_identifiers.append(d[0].lower())
    secret_level_paths.append(d[1])
    secret_solution_paths.append(d[2])
    secret_solutions.append(d[3])
    secret_unpw.append(d[4])
    secret_rating.append(d[5])
    secret_reach.append((d[6], d[7]))

secret_count = len(secret_names)
role_secret_solve = []
role_color = []
for i in range(secret_count):
    role_secret_solve.append('solved-' + secret_identifiers[i])
    role_color.append('color-' + secret_identifiers[i])
    
ac_names = []
ac_descriptions = []
ac_paths = []
cursor.execute('select name, description, path from achievements order by id')
data = cursor.fetchall()
for d in data:
    ac_names.append(d[0])
    ac_descriptions.append(d[1])
    ac_paths.append(d[2])
    
@bot.event
async def on_ready():
    print(f'{bot.user} has connected to Discord!')
    global guild
    guild = discord.utils.get(bot.guilds, name='The String Harmony')
    
@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.errors.MissingRequiredArgument):
        await ctx.send('Invalid command...')
        
@bot.event
async def on_member_update(before, after):
    n = after.nick
    if n == None:
        n = after.global_name
    role = None
    role_id = -1
    while (not role) and (role_id < (level_count - 1)):
        role_id = role_id + 1
        role = discord.utils.get(after.roles, name=role_list[role_id])
    if role:
        if role_id == (level_count - 1):
            newn = ' ' + medal
        else:
            newn = ' [' + level_names[role_id+1] + ']'
        if n.find(newn) == -1:
            finaln = n[:max_namelen] + newn
            await after.edit(nick=finaln)
            cursor.execute('update users set nickname = %s where id = %s', (n[:max_namelen], after.id))
            connection.commit()

@bot.command(name='sync')
async def sync(ctx):
    member = guild.get_member(ctx.author.id)
    if not member.guild_permissions.administrator:
        return
    insert, update, insert_secrets = [], [], []
    cursor.execute('select id from users')
    ids = set(cursor.fetchall())
    cursor.execute('select user_id, level_id from secret_solves')
    secret_solves = set(cursor.fetchall())
    for member in guild.members:
        role = None
        role_id = -1
        while (not role) and (role_id < (level_count - 1)):
            role_id = role_id + 1
            role = discord.utils.get(member.roles, name=role_list[role_id])
        if not role:
            continue
        if role_id == level_count - 1:
            name = member.nick[:-1-len(medal)]
        else:
            name = member.nick[:-3-len(level_names[role_id + 1])]
        if (member.id,) in ids:
            update.append((name, role_id + 2, member.id))
        else:
            insert.append((member.id, name, role_id + 2))
        for level_id in range(secret_count):
            role = discord.utils.get(member.roles, name=role_secret_solve[level_id])
            if role and (member.id, level_id + 1) not in secret_solves:
                insert_secrets.append((member.id, level_id + 1))
    psycopg2.extras.execute_batch(cursor, 'update users set nickname = %s, current_level = %s where id = %s', update)
    psycopg2.extras.execute_batch(cursor, 'insert into users (id, nickname, current_level) values (%s, %s, %s)', insert)
    psycopg2.extras.execute_batch(cursor, 'insert into secret_solves (user_id, level_id) values (%s, %s)', insert_secrets)
    connection.commit()
    await ctx.send('Database sync completed!')
    
@bot.command(name='send')
async def send(ctx,channel_name,message):
    member = guild.get_member(ctx.author.id)
    if member.guild_permissions.administrator:
        channel = discord.utils.get(guild.channels, name=channel_name)  
        await channel.send(message)
        await ctx.send('Message sent!')
    else:
        await ctx.send('I only listen to the creator!')

@bot.command(name='reach',help='Register the solution pages you reached')
async def reach(ctx,ans):
    if ctx.guild and not ctx.message.author.guild_permissions.administrator:
        author = ctx.message.author
        await ctx.message.delete()
        text = 'I only listen to you in PM!'
        await author.send(text)
    else:
        id = ctx.author.id
        if ans in level_paths:
            await solve(id,ans)
        elif ans in secret_level_paths or ans in secret_solution_paths:
            await secret(id,ans)
        if ans in ac_paths:
            await achievement(id, ans)
    
@bot.command(name='recall',help='Show info of the levels you reached/solved')
async def recall(ctx,level):
    member = guild.get_member(ctx.author.id)
    if ctx.guild and not ctx.message.author.guild_permissions.administrator:
        author = ctx.message.author
        await ctx.message.delete()
        text = 'I only listen to you in PM!'
        await author.send(text)
    elif level in level_names:
        level_id = level_names.index(level)
        role = None
        role_id = -1
        while (not role) and (role_id < (level_count - 1)):
            role_id = role_id + 1
            role = discord.utils.get(member.roles, name=role_list[role_id])
        if ((not role) and (level_id > 0)) or (role and role_id < (level_id - 1)):
            await ctx.send('You haven\'t reached the level!')
        else:
            unpw = len(unpw_id) - 1
            while (unpw >= 0) and (unpw_id[unpw] >= level_id):
                unpw = unpw - 1
            output = 'https://thestringharmony.com' + level_paths[level_id]
            if unpw == -1:
                output += '\nUN/PW: `None`'
            else:
                output += '\nUN/PW: `' + unpw_answers[unpw] + '`'
            if role and role_id >= level_id:
                output += '\nSolution: `' + level_solutions[level_id] + '`'
            await ctx.send(output)
    elif level in secret_identifiers:
        level_id = secret_identifiers.index(level)
        role_reach = discord.utils.get(member.roles, name=secret_reach[level_id][0])
        role_solve = discord.utils.get(member.roles, name=role_secret_solve[level_id])
        if not role_reach and not role_solve:
            await ctx.send('You haven\'t reached the level!')
        else:
            output = 'https://thestringharmony.com' + secret_level_paths[level_id]
            output += '\nUN/PW: `' + secret_unpw[level_id] + '`'
            if role_solve:
                output += '\nSolution: `' + secret_solutions[level_id] + '`'
            await ctx.send(output)
    else:
        await ctx.send('Wrong level name!')

@bot.command(name='continue',help='Show info of the main level you are on')
async def continue_main(ctx):     
    member = guild.get_member(ctx.author.id)
    if ctx.guild and not ctx.message.author.guild_permissions.administrator:
        author = ctx.message.author
        await ctx.message.delete()
        text = 'I only listen to you in PM!'
        await author.send(text)
        return
    role = None
    role_id = -1
    while (not role) and (role_id < (level_count - 1)):
        role_id = role_id + 1
        role = discord.utils.get(member.roles, name=role_list[role_id])
    if role and role_id == level_count - 1:
        await ctx.send('You have completed the game!')
        return
    if role:
        level_id = role_id + 1
    else:
        level_id = 0
    unpw = len(unpw_id) - 1
    while (unpw >= 0) and (unpw_id[unpw] >= level_id):
        unpw = unpw - 1
    output = 'https://thestringharmony.com' + level_paths[level_id]
    if unpw == -1:
        output += '\nUN/PW: `None`'
    else:
        output += '\nUN/PW: `' + unpw_answers[unpw] + '`'
    await ctx.send(output)          
        
@bot.command(name='stat',help='Show player statistics')
async def stat(ctx):
    num = []
    num.append(len([m for m in guild.members if not m.bot and not m.guild_permissions.administrator]))
    for i in range(len(mile_id)):
        role = discord.utils.get(guild.roles, name=mile_role[i])
        num.append(len(role.members))
        num[i] = num[i] - num[i+1]
    output = 'Player statistics:'
    output += '\nNone: ' + str(num[0])
    for i in range(len(mile_id)):
        output = output + '\n' + mile_role[i] + ': ' + str(num[i + 1])
    await ctx.send(output)
    
@bot.command(name='color',help='Change the color of your name')
async def color(ctx,level):
    member = guild.get_member(ctx.author.id)
    rolef9 = discord.utils.get(member.roles, name='solved-f9')
    roled = discord.utils.get(member.roles, name='solved-d')
    if rolef9 or roled:
        if level in secret_identifiers:
            secret_id = secret_identifiers.index(level)
            roles = discord.utils.get(member.roles, name=role_secret_solve[secret_id])
            if roles:
                role = None
                role_id = -1
                while (not role) and (role_id < (secret_count - 1)):
                    role_id = role_id + 1
                    role = discord.utils.get(member.roles, name=role_color[role_id])
                if role:
                    await member.remove_roles(role)
                role = discord.utils.get(guild.roles, name=role_color[secret_id])
                await member.add_roles(role)
                await ctx.send('Username color updated!')
            else:
                await ctx.send('You haven\'t solved the level!')
        else:
            await ctx.send('Wrong secret level name!')
    else:
        await ctx.send('You aren\'t permitted to change your username color!')
            
async def solve(id,ans):
    level_id = level_paths.index(ans) - 1
    level = level_names[level_id]
    member = guild.get_member(id)
    if level_id > 0:
        role = discord.utils.get(member.roles, name=role_list[level_id-1])
    else:
        role = False
    if (level_id == 0 and len(member.roles) == 1) or role:
        if role:
            await member.remove_roles(role)
            n = member.nick[:-3-len(level)]
        else:
            n = member.nick
            if n == None:
                n = member.global_name
        await member.edit(nick=n[:max_namelen])
        if level_id == (level_count - 1):
            output = 'You have successfully solved level ' + '**' + level + '**!\n' \
            + 'You have **completed** the game. Congrats!! ' + medal
        else:
            role = discord.utils.get(guild.roles, name=role_list[level_id])
            await member.add_roles(role)
            output = 'You have successfully solved level ' + '**' + level + '**!'
        await member.send(output)
        for mile in range(len(mile_id)):
            if level_id == mile_id[mile]:
                role = discord.utils.get(guild.roles, name=mile_role[mile])
                await member.add_roles(role)
                channel = discord.utils.get(guild.channels, name=level_names[mile_id[mile]])
                output = '<@' + str(member.id) + '> has completed level **' + level_names[mile_id[mile]] + '**' \
                + ' and become one of **@' + mile_role[mile] + '**. Congrats!!'
                await channel.send(output)
        cursor.execute('update users set current_level = %s where id = %s', (level_id + 2, id))
        connection.commit()
                
async def secret(id,ans):
    member = guild.get_member(id)
    if ans in secret_solution_paths:
        level_id = secret_solution_paths.index(ans)
        level = secret_names[level_id]
        role_reach = discord.utils.get(member.roles, name=secret_reach[level_id][0])
        role_solve = discord.utils.get(member.roles, name=role_secret_solve[level_id])
        if role_reach and not role_solve: 
            role = discord.utils.get(guild.roles, name=role_secret_solve[level_id])
            await member.add_roles(role)
            output = 'You have successfully solved level ' + '**' + level + '**!'
            await member.send(output)
            channel_name = secret_identifiers[level_id]
            channel = discord.utils.get(guild.channels, name=channel_name)
            output = '<@' + str(member.id) + '> has completed level **' + level + '**. Congrats!!'
            await channel.send(output)
            if secret_reach[level_id][1]:
                await member.remove_roles(role_reach)
            cursor.execute('insert into secret_solves (user_id, level_id) values (%s, %s)', (id, level_id + 1))
            connection.commit()
    if ans in secret_level_paths:
        level_id = secret_level_paths.index(ans)
        role = discord.utils.get(member.roles, name=secret_reach[level_id][0])
        if not role:
            role = discord.utils.get(guild.roles, name=secret_reach[level_id][0])
            await member.add_roles(role)

async def achievement(id,ans):
    ac_id = ac_paths.index(ans)
    cursor.execute('select * from achievement_finds where user_id = %s and achievement_id = %s', (id, ac_id + 1))
    if not cursor.fetchone():
        ac = ac_names[ac_id]
        member = guild.get_member(id)
        output = 'Achievement: **' + ac + '**'
        output += '\n*' + ac_descriptions[ac_id] + '*'
        output += '\nhttps://thestringharmony.com' + ans
        img = 'cheevos/' + ac + '.jpg'
        await member.send(output,file=discord.File(img))
        cursor.execute('insert into achievement_finds (user_id, achievement_id) values (%s, %s)', (id, ac_id + 1))
        connection.commit()

@app.after_request
def header(response):
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Headers'] = '*'
    return response

@app.route('/', methods=['POST'])
async def handle():
    session_id = (await request.get_json())["session"]
    cursor.execute('select id from users where session = %s', (session_id,))
    result = cursor.fetchone()
    if not result:
        return 'OK', 200
    id = result[0]
    ans = (await request.get_json())["ans"]
    if ans in level_paths:
        await solve(id,ans)
    elif ans in secret_level_paths or ans in secret_solution_paths:
        await secret(id,ans)
    if ans in ac_paths:
        await achievement(id,ans)
    return 'OK', 200
    
@app.route('/login')
async def login():
    code = request.args.get('code')
    data = {
        'client_id': '859512367480963103',
    	'client_secret': '',
        'grant_type': 'authorization_code',
        'redirect_uri': 'http://the-string-harmony-bot.herokuapp.com/login',
        'scope': 'identify',
        'code': code
    }
    response = requests.post('https://discordapp.com/api/oauth2/token', data=data).json()
    access_token = response['access_token']
    headers = {
        'authorization': f'Bearer {access_token}'
    }
    response = requests.get('https://discord.com/api/users/@me', headers=headers).json()
    id = int(response['id'])
    while True:
        session_id = ''.join(random.choices('abcdefghijklmnopqrstuvwxyz0123456789', k=32))
        cursor.execute('select session from users where session = %s', (session_id,))
        if not cursor.fetchone():
            break
    cursor.execute('select id from users where id = %s', (id,))
    if cursor.fetchone():
        cursor.execute('update users set session = %s where id = %s', (session_id, id))
    else:
        member = guild.get_member(id)
        if member.nick:
            name = member.nick
        else:
            name = response['global_name']
        cursor.execute('insert into users (id, session, nickname, current_level) values (%s, %s, %s, %s)', (id, session_id, name, 1))
    connection.commit()
    redirection = await make_response(redirect('https://thestringharmony.com/login/?session=' + session_id))
    return redirection

@app.route('/leaderboard')
def leaderboard():
    cursor.execute('''
        select rank() over(order by levelno desc, bonus desc) as rank,
        name, level, secrets, bonus
        from (
        select nickname as name, current_level as levelno, mains.name as level,
        array_agg(secret_solves.level_id order by secret_solves.level_id) as secrets,
        coalesce(sum(secrets.rating), 0) as bonus
        from users
        join mains on users.current_level = mains.id
        left join secret_solves on users.id = secret_solves.user_id
        left join secrets on secret_solves.level_id = secrets.id
        group by nickname, users.current_level, mains.name) as leaderboard
        order by rank
    ''')
    return cursor.fetchall()

@app.route('/secret_info')
def secret_info():
    cursor.execute('select name, color from secrets order by id')
    return cursor.fetchall()

@app.route('/achievement_info')
def achievement_info():
    cursor.execute('select name, description from achievements order by id')
    return cursor.fetchall()

@app.route('/retrieve', methods=['POST'])
async def retrieve():
    session_id = (await request.get_json())["session"]
    cursor.execute('select id, nickname, current_level from users where session = %s', (session_id,))
    result = cursor.fetchone()
    if not result:
        return 'Fail', 404
    id = result[0]
    member = guild.get_member(id)
    response = {}
    response['nickname'] = result[1]
    response['mains'] = []
    unpw_pt = -1
    for i in range(min(result[2], level_count)):
        if i > unpw_id[unpw_pt + 1]:
            unpw_pt += 1
        if unpw_pt < 0:
            unpw = 'None'
        else:
            unpw = unpw_answers[unpw_pt]
        if i == result[2] - 1:
            solution = '-'
        else:
            solution = level_solutions[i]
        response['mains'].append((level_names[i], level_paths[i], unpw, solution))
    response['secrets'] = []
    for i in range(secret_count):
        role_reach = discord.utils.get(member.roles, name=secret_reach[i][0])
        role_solve = discord.utils.get(member.roles, name=role_secret_solve[i])
        if not role_reach and not role_solve:
            continue
        if role_solve:
            solution = secret_solutions[i]
        else:
            solution = '-'
        response['secrets'].append((secret_names[i], secret_level_paths[i], secret_unpw[i], solution, secret_rating[i]))
    cursor.execute('''
        select name, description, path from achievements
        join achievement_finds on achievement_finds.achievement_id = achievements.id
        where user_id = %s
        order by achievements.id
    ''', (id,))
    response['achievements'] = cursor.fetchall()
    return response, 200

@app.route('/retrieve_id', methods=['POST'])
async def retrieve_id():
    session_id = (await request.get_json())["session"]
    cursor.execute('select id from users where session = %s', (session_id,))
    result = cursor.fetchone()
    if result:
        return str(result[0]), 200
    else:
        return '-1', 200

async def main():
    port = int(os.environ.get("PORT", 5000))
    async with bot:
        bot.loop.create_task(app.run_task(host='0.0.0.0',port=port))
        await bot.start(TOKEN)

asyncio.run(main())