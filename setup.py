import os
import os.path
import sys

SYSTEMD_SERVICE_TEMPLATE = '''
[Unit]
Description = bridge service
After       = network.target

[Service]
Type=forking
WorkingDirectory={install_dir}
ExecStart=/usr/bin/python3 bridge.py

# In case if it gets stopped, restart it immediately
Restart     = always

Type        = simple


[Install]
# multi-user.target corresponds to run level 3
# roughtly meaning wanted by system start
WantedBy    = multi-user.target
'''


def setup_autostart():
    print('Setting up bridge autostart: tmp/bridge.service')
    with open('tmp/bridge.service', 'w') as service_file:
        service_file.write(
            SYSTEMD_SERVICE_TEMPLATE.format(install_dir=os.getcwd()))

    run('sudo systemctl stop bridge.service', die_on_fail=False)
    run('sudo cp tmp/bridge.service /etc/systemd/system')
    run('sudo systemctl daemon-reload')
    run('sudo systemctl enable bridge.service')
    run('sudo systemctl start bridge.service')
    print('bridge.service has been set to automatically start up at boot time.')


def run(command, die_on_fail=True):
    print('Running: {command}'.format(command=command))
    if os.system(command) == 0:
        return True

    sys.stderr.write(
        'error: Operation failed: {command}\n'.format(command=command))
    if die_on_fail:
        exit(255)

    return False


if __name__ == '__main__':
    setup_autostart()
