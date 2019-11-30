def cmd(cmd, event):
    import psutil
    import time
    import os
    p = psutil.Process(os.getpid())
    
    event.message_send('Заюзано:\n\t{} МБ\n\t{}% ЦП\n\tРабота: {} часа'.format(round(p.memory_info()[0] / 1024**2, 1), p.cpu_percent(interval=1), round((time.time() - event.bot.launched)/3600, 1)), event.peer_id) 
    
    del p, os, time, psutil

def launch(bot):
    import time
    bot.launched = time.time()
    del time
