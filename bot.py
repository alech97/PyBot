'''
Created on Aug 18, 2017
@author: Alec Helyar
@version: 2017.8.18
'''
import io
import time
import queue as q
import discord
import settingsLoader
import multiprocessing
from contextlib import redirect_stdout

def limit(string, length = 2000):
    return string if len(string) <= length else string[:length]

def print_lines(string):
    return ''.join(['>>>' + line + '\n' for line in string.splitlines()])

def run(queue, command):
    print("run:", command)
    f = io.StringIO()
    with redirect_stdout(f):
        try:
            exec(compile(command, 'bot.py', 'exec'))
        except Exception as e:
            queue.put(str(e))
            return
    msg = f.getvalue()
    if len(msg) > 200:
        msg = msg[:200] + '...'
    if msg and len(msg):
        queue.put(print_lines(msg))
    else:
        queue.put(">>>No output.  Did you forget to print()?")

if __name__ == '__main__':
    client = discord.Client()
    settings = settingsLoader.Settings('config.txt')

    @client.event
    async def on_ready():
        print('Logged in as')
        print(client.user.name)
        print(client.user.id)
        print('------')

    def start_run(queue, channel, command):
        p = multiprocessing.Process(target=run, name="Runner", args=(queue, command,))
        p.start()
        return p

    @client.event
    async def on_message(message):
        if (message.content.startswith('python ')):
            command = message.content[7:]
            print(command)
            queue = multiprocessing.Queue(1)
            p = start_run(queue, message.channel, command)
            #Try to pull from queue but wait for its completion
            try:
                msg = queue.get(True, timeout=2)
            except q.Empty:
                msg = ">>>No output. It may have timed out."
            finally:
                p.terminate()
            print(msg)
            try:
                await client.send_message(message.channel, limit(msg))
            except Exception as e:
                client.send_message(message.channel, limit(str(e)))
                print("Error in HTTP Request", e)

    client.run(settings.get_token())
