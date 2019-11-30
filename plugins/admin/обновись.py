def cmd(cmd, event):
    from main import load, cmds
    
    cmds.update(load(cmds))
    
    event.message_send('Done')
