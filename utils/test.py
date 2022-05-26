from curses import echo
import re
from fabric import Connection
import paramiko

run_cmd = Connection(
    f"meduser@10.41.3.2").run(f"cd /var/www/BHT-Core && git describe", hide=True, echo=True)

print("{0.stdout}".format(run_cmd).strip())
