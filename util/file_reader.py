from pathlib import Path
import asyncio

project_root = Path(__file__).parent.parent
template_dir = project_root / "templates"

async def do_line_by_line(function,filename:str,character_delay:float=0.05,delay:float=.5):
    with open(template_dir/filename, 'r') as file:
        for line in file:
            await asyncio.sleep(len(line) * character_delay + delay)
            line = line.strip()
            if line == "":
                continue
            await function(line)
    file.close()
    await asyncio.sleep(1)
