import discord
import asyncio
from discord.ext import commands

#OBS: ESTE CÓDIGO CONTÉM ALTO NÍVEL DE GAMBIARRA...

#É importante que as intents estejam ativadas.

#Não é feito em cogs, mas é fácil adaptá-lo.

client = commands.Bot(command_prefix='Prefixo', intents=discord.Intents.all())

votações = {}

@client.command()
@commands.cooldown(1, 600, commands.BucketType.user)
async def voteban(ctx, membro : discord.Member, quant : int, *, razão=None):
    #Faz as verificações necessárias para que não hajam abusos
    #Se a razão estiver vazia
    if razão == None:
        await ctx.send('Especifique a razão')
        voteban.reset_cooldown(ctx)
        return False
    #Se o autor for um bot
    if membro.bot == True:
        await ctx.send(f'Você não pode abrir votação para um bot {ctx.author.mention}!')
        voteban.reset_cooldown(ctx)
        return False
    #Se o membro ter uma role mais alta que o autor da mensagem
    if membro.top_role > ctx.author.top_role:
        await ctx.send(f'Você não pode abrir votação para alguém com cargo superior ao seu {ctx.author.mention}!')
        voteban.reset_cooldown(ctx)
        return False
    #Se a quantidade de votos ser menor que 3 (Eu botei esta quantidade pois acho uma boa quantidade minima mas caso queira tirar esta parte você pode tirar)
    if quant < 3:
        await ctx.send(f'O número de votos necessários deve ser maior que 3!')
        voteban.reset_cooldown(ctx)
        return False
    #Cria a embed
    embed = discord.Embed(title='VOTE BAN 💣', description=f'Vote ban {membro.mention} 0/{quant}', color=discord.Color.from_rgb(255, 0, 0))
    embed.add_field(name='Motivo', value=razão)
    embed.set_footer(text=f'Solicitado por {ctx.author}')
    #Manda a embed e adiciona a reação para voto
    msg = await ctx.send(embed=embed)
    await msg.add_reaction('⛏')
    #Registra as informações necessárias no dict (Pode ser adaptado para outros tipos de armazenamento)
    votações[f'{msg.id}'] = {}
    votações[f'{msg.id}']['membro'] = membro
    votações[f'{msg.id}']['objetivo'] = quant
    votações[f'{msg.id}']['count'] = 0
    votações[f'{msg.id}']['razão'] = razão
    votações[f'{msg.id}']['solicitante'] = ctx.author
    votações[f'{msg.id}']['total'] = []
    #Espera 1 hora para verificar se a votação atingiu o objetivo
    await asyncio.sleep(3600)
    try:
        try:
            #Caso não tenha atingido ele edita a embed para uma embed de cancelamento de votação
            votações[f'{msg.id}']
            embedfalho = discord.Embed(title='❌ VOTE BAN CANCELADO', description=f'Votação de kick para {membro}')
            await msg.edit(embed=embedfalho)
            votações.__delitem__(f'{msg.id}')
        except:
            #Caso contrário
            pass
    except:
        pass

#Parte mais importante
@client.event
async def on_reaction_add(reaction, user):
    if user.id == client.user.id:
        pass
    else:
        #Se a reação for igual á reação que adicionamos anteriormente
        if str(reaction.emoji) == '⛏':
            #Puxa os dados e define como a variável "verificar" (Eu preferi fazer isto para simplificar um pouco o trabalho)
            verificar = votações[f'{reaction.message.id}']
            #Se a mensagem da reação for igual á uma mensagem do bot
            if reaction.message.author.id == client.user.id:
                #Se o usuário não for um bot
                if user.bot == False:
                    try:
                        #Se o usuário já ter votado (Para não ocorrer o bug de "farm" de votos)
                        if user.id in verificar['total']:
                            #Cancela todas as ações que iriam vir á seguir
                            return False
                    except:
                        pass
                    #Chaves do dict marcadas como variáveis (Novamente para simplificar o trabalho)
                    count = verificar['count']
                    membro = verificar['membro']
                    quant = verificar['objetivo']
                    razão = verificar['razão']
                    solicitante = verificar['solicitante']
                    #Embed bonitinha
                    embed = discord.Embed(title='VOTE BAN 💣',
                                          color=discord.Color.from_rgb(255, 0, 0))
                    embed.add_field(name='Motivo', value=razão)
                    embed.set_footer(text=f'Solicitado por {solicitante}')
                    #Adicionar mais um número á quantidade de votos
                    verificar['count'] = count + 1
                    #Adicionar o usuário ao total para não ocorrer o "farm" de votos.
                    verificar['total'].append(user.id)
                    #Descrição com a quantidade de votos atual / quantidade de votos objetivo.
                    embed.description = f'Vote ban {membro.mention} {verificar["count"]}/{quant}'
                    #Se a contagem tiver atingido o objetivo
                    if verificar['count'] == verificar[f'objetivo']:
                        #Edita a embed
                        await reaction.message.edit(embed=embed)
                        #Cria uma lista para o registro das roles com a perm de ADM
                        listas = []
                        for role in user.guild.roles:
                            #Se a role for uma role de bot
                            if role.is_bot_managed() == True:
                                pass
                            #Caso contrário
                            else:
                                #Se a role tiver perm de ADM
                                if role.permissions.administrator == True:
                                    #Adiciona a role á lista
                                    listas.append(role)
                                #Se a role tiver perm de banir membros
                                else:
                                    if role.permissions.ban_members == True:
                                        #Adiciona a role á lista
                                        listas.append(role)
                        #Envia a mensagem pedindo permissão para os adms
                        msg2 = await reaction.message.reply('Aguardando algum moderador aprovar a votação... (')
                        #Para cada role na lista edita a mensagem e menciona a role (ATENÇÃO: ESTA PARTE PODE SER ADAPTADA E É IMPORTANTE QUE SEJA POIS PODE PROVOCAR RATE LIMIT, COMO FALEI ANTERIORMENTE CONTÉM MUITAS GAMBIARRAS NO CÓDIGO)
                        for m in listas:
                            await msg2.edit(content=f'{msg2.content} {m.mention}')
                        #Finaliza o conteúdo da mensagem com um ")"
                        await msg2.edit(content=f'{msg2.content})')
                        #Adiciona a reação de confirmação
                        await msg2.add_reaction('✅')

                        #Check
                        def check2(re, us):
                            return str(re.emoji) == '✅' and us.top_role in listas and us.bot == False
                        #Wait_for
                        try:
                            r, u = await client.wait_for('reaction_add', check=check2, timeout=3600)
                        #Se o tempo de espera pela confirmação acabar
                        except asyncio.TimeoutError:
                            #Edita a embed para votação encerrada
                            await msg2.reply(':negative_squared_cross_mark: Votação encerrada, sem aprovação.')
                            await reaction.message.delete()
                            votações.__delitem__(f'{reaction.message.id}')
                            return False
                        #Caso seja confirmado o membro é banido
                        await membro.ban(
                            reason=f'Vote kick iniciado por {solicitante}\nmotivo: {razão}\nAprovado por: {u}')
                        #Responde a mensagem do bot com a confirmação do banimento
                        await reaction.message.reply(
                            f'O membro {membro.mention} foi banido!\nAprovado por: {u.mention}')
                        await msg2.delete()
                        #Tira todos os itens da votação do dict (Para aliviar um pouco o código também)
                        votações.__delitem__(f'{reaction.message.id}')
                    await reaction.message.edit(embed=embed)


client.run('token')
