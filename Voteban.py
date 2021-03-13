import discord
from discord.ext import commands

client = commands.Bot(command_prefix='Prefixo', intents=discord.Intents.all())

votações = {}

@client.command()
@commands.cooldown(1, 600, commands.BucketType.user)
async def voteban(ctx, membro : discord.Member, quant : int, *, razão=None):
    if razão == None:
        await ctx.send('Especifique a razão')
        voteban.reset_cooldown(ctx)
        return False
    if membro.bot == True:
        await ctx.send(f'Você não pode abrir votação para um bot {ctx.author.mention}!')
        voteban.reset_cooldown(ctx)
        return False
    if membro.top_role > ctx.author.top_role:
        await ctx.send(f'Você não pode abrir votação para alguém com cargo superior ao seu {ctx.author.mention}!')
        voteban.reset_cooldown(ctx)
        return False
    if quant < 3:
        await ctx.send(f'O número de votos necessários deve ser maior que 3!')
        voteban.reset_cooldown(ctx)
        return False
    embed = discord.Embed(title='VOTE BAN 💣', description=f'Vote ban {membro.mention} 0/{quant}', color=discord.Color.from_rgb(255, 0, 0))
    embed.add_field(name='Motivo', value=razão)
    embed.set_footer(text=f'Solicitado por {ctx.author}')
    msg = await ctx.send(embed=embed)
    await msg.add_reaction('⛏')
    votações[f'{msg.id}'] = {}
    votações[f'{msg.id}']['membro'] = membro
    votações[f'{msg.id}']['objetivo'] = quant
    votações[f'{msg.id}']['count'] = 0
    votações[f'{msg.id}']['razão'] = razão
    votações[f'{msg.id}']['solicitante'] = ctx.author
    await asyncio.sleep(3600)
    try:
        embedfalho = discord.Embed(title='❌ VOTE BAN CANCELADO', description=f'Votação de kick para {membro}')
        await msg.edit(embed=embedfalho)
        votações.__delitem__(f'{msg.id}')
    except:
        pass

@client.event
async def on_reaction_add(reaction, user):
    if user.id == client.user.id:
        pass
    else:
        if str(reaction.emoji) == '⛏':
            if reaction.message.author.id == client.user.id:
                if user.bot == False:
                    verificar = votações[f'{reaction.message.id}']
                    count = verificar['count']
                    membro = verificar['membro']
                    quant = verificar['objetivo']
                    razão = verificar['razão']
                    solicitante = verificar['solicitante']
                    embed = discord.Embed(title='VOTE BAN 💣',
                                          color=discord.Color.from_rgb(255, 0, 0))
                    embed.add_field(name='Motivo', value=razão)
                    embed.set_footer(text=f'Solicitado por {solicitante}')
                    verificar['count'] = count + 1
                    embed.description = f'Vote ban {membro.mention} {verificar["count"]}/{quant}'
                    if verificar['count'] == verificar[f'objetivo']:
                        await reaction.message.edit(embed=embed)
                        listas = []
                        for role in user.guild.roles:
                            if role.is_integration == True:
                                pass
                            else:
                                if role.permissions.administrator == True:
                                    if role.name == 'DG Team':
                                        pass
                                    else:
                                        listas.append(role)
                                else:
                                    if role.permissions.ban_members == True:
                                        listas.append(role)
                        msg2 = await reaction.message.reply('Aguardando algum moderador aprovar a votação... (')
                        for m in listas:
                            await msg2.edit(content=f'{msg2.content} {m.mention}')
                        await msg2.edit(content=f'{msg2.content})')
                        await msg2.add_reaction('✅')

                        def check2(re, us):
                            return str(re.emoji) == '✅' and us.top_role in listas and us.bot == False
                        try:
                            r, u = await client.wait_for('reaction_add', check=check2, timeout=3600)
                        except asyncio.TimeoutError:
                            await msg2.reply(':negative_squared_cross_mark: Votação encerrada, sem aprovação.')
                            await reaction.message.delete()
                            votações.__delitem__(f'{reaction.message.id}')
                            return False
                        await membro.ban(
                            reason=f'Vote kick iniciado por {solicitante}\nmotivo: {razão}\nAprovado por: {u}')
                        await reaction.message.reply(
                            f'O membro {membro.mention} foi banido!\nAprovado por: {u.mention}')
                        await msg2.delete()
                    await reaction.message.edit(embed=embed)

client.run('token')
