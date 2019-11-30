def cmd(cmd, event):
    import random
    
    res = event.bot.method('docs.search', **{'count': 200, 'adult': 1, 'q': ' '.join(event.text.split()[2:]), 'v': '5.68'}, type='POST')
    
    info = []

    if (res['response']['count'] != 0):
        for k in range(len(res['response']['items'])):
            for i in range(10):
                itm = random.randint( 0, len(res['response']['items'])-1)
                title = res['response']['items'][itm]['title'].lower()

                info.append('doc'+str(res['response']['items'][itm]['owner_id'])+'_'+str(res['response']['items'][itm]['id']))

        event.message_send('Доки по запросу {}(всего: {})'.format(event.argue, len(res['response']['items'])), event.peer_id, attachment=",".join(info))
    else:
        event.message_send('Доки по запросу {} не найдены'.format(event.argue), event.peer_id)
