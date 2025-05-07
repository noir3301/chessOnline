import subprocess


processes = [subprocess.Popen(["python", 'main.py', 'debug', 'host']),
             subprocess.Popen(["python", 'main_second_win.py', 'debug', 'client'])]
stdouts, stderrs = [None, None], [None, None]
stdouts[0], stderrs[0] = processes[0].communicate()
stdouts[1], stderrs[1] = processes[1].communicate()