def threading():
    return True

def cmd(cmd, event):
    event.message_send(str(eval(event.argue)))
