# Bridge

Bridge is a collection of scripts that help you export various metrices of remote hosts to a central data repo.

## Why we wrote Bridge?

We manage over ~800 remote hosts running Electronic Medical Record Systems (EMRS) somewhere in Africa! Each EMRS site is independent - with some sites connected to a central hub over an intermittent VPN connection. We wrote bridge to collect EMRS version data for connected sites. And got a little bit carried away and started exporting more metrices.

## Alternatives

Depending on your environment, you can use better monitoring systems (like Prometheus).

## Installation

This section will walk you through setting up Bridge on an Ubuntu 20.04 server.

1. Set up a virtual environment for Bridge. You can follow instruction on how to set up a virtual environment here: <https://www.digitalocean.com/community/tutorials/how-to-install-python-3-and-set-up-a-programming-environment-on-ubuntu-20-04-quickstart>.

2. Provide your environment variable in the .env

```bash
mv .env.example .env
vim .env
```

3. Install required packages.

```python
pip install -r requirements.txt
```

4. All exporters are in exporters directory. You can choose to set up cron jobs for the exporters to schedule when they should run. You can read more on how to set up a cron job here: <https://www.digitalocean.com/community/tutorials/how-to-use-cron-to-automate-tasks-ubuntu-1804>. To manually run an exporter (e.g. running the version exporter):

```bash
cd exporters
python3 version_exporter.py
```
