import numpy as np
import pandas as pd

class Runner:
    def __init__(self, client, channel):
        self.client = client
        self.channel = channel

    async def run_command(self, command):
        print("Reached:", command)
        f = io.StringIO()
        with redirect_stdout(f):
            try:
                exec(command)
            except Exception as e:
                return str(e)
        msg = f.getvalue()
        if msg and len(msg):
            await self.client.send_message(self.channel, self.print_lines(msg))
        else:
            await self.client.send_message(self.channel, '>>>No output')

    
