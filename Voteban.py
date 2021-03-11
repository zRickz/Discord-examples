import discord
from discord import commands

client = commands.Bot(command_prefix='prefixo do seu bot', intents=discord.Intents.all())

@client.command()
@commands.cooldown(1, 600, commands.BucketType.user)
async def voteban(ctx, membro : discord.Member, quant : int, *, razão=None):
    if razão == None:
        await ctx.send('Especifique a razão')
        return False
    def check(react, user):
        return str(user.bot) == 'False' and str(react.emoji) == '⛏'

    embed = discord.Embed(title='VOTE BAN 💣', description=f'Vote ban {membro.mention} 0/{quant}', color=discord.Color.from_rgb(255, 0, 0))
    embed.add_field(name='Motivo', value=razão)
    embed.set_footer(text=f'Solicitado por {ctx.author}')
    msg = await ctx.send(embed=embed)
    await msg.add_reaction('⛏')
    async def aguardar():
        def check(react, user):
            return str(user.bot) == 'False' and str(react.emoji) == '⛏'
        react, user = await client.wait_for('reaction_add', check=check)
        global count
        count = 0
        count += 1
        embed.description = f'Vote ban {membro.mention} {count}/{quant}'
        await msg.edit(embed=embed)
        return count
    retornador = await aguardar()
    if retornador == quant:
        listas = []
        for role in ctx.guild.roles:
            if role.permissions.administrator == True:
                if role.name == 'DG Team':
                    pass
                else:
                    listas.append(role)
            else:
                if role.permissions.ban_members == True:
                    listas.append(role)
        msg2 = await ctx.send('Aguardando algum moderador aprovar a votação... (')
        for m in listas:
            await msg2.edit(content=f'{msg2.content} {m.mention}')
        await msg2.edit(content=f'{msg2.content})')
        await msg2.add_reaction('✅')
        def check2(re, us):
            return str(re.emoji) == '✅' and us.top_role in listas
        r, u = await client.wait_for('reaction_add', check=check2, timeout=86400)
        await membro.ban(reason=f'Vote kick iniciado por {ctx.author}\nmotivo: {razão}\nAprovado por: {u}')
        await msg.reply(f'O membro {ctx.author} foi banido!\nAprovado por: {ctx.author.mention}')
        await msg2.delete()
        listas.clear()
        pass
    else:
        contador = await aguardar()
        await aguardar()

client.run(token)
