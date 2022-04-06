
# Bridge

![example workflow](https://github.com/DoxDevOps/bridge/actions/workflows/python-package.yml/badge.svg)

Bridge is a collection of scripts that help you export various metrices from hosts within your local network to a cloud central data repo.

## Why did we write Bridge?

We manage over ~800 hosts running Electronic Medical Record Systems (EMRS) somewhere in Africa! We wrote bridge to collect and export EMRS version data to a cloud data repo. This data is then visualized for stakeholders that don't have access to our local network. P.S. we got a little bit carried away and started exporting more metrices other than just version details.

## How does Bridge work?

1. We have a database of details of all hosts within our network. Thus, ip addresses, hostnames, etc. The data in this database is accessible via a simple REST API.
2. An exporter gets these host details, loops through them and collect relevant data
3. This data is then sent to a cloud data repo for visualization

## Installation

This section will walk you through setting up Bridge on an Ubuntu 20.04 server.

1. Clone the repo

```bash
git clone https://github.com/DoxDevOps/bridge.git
```

2. Set up a virtual environment for Bridge. You can follow instruction on how to set up a virtual environment here: <https://www.digitalocean.com/community/tutorials/how-to-install-python-3-and-set-up-a-programming-environment-on-ubuntu-20-04-quickstart>.

3. Provide your environment variables in the .env

```bash
mv .env.example .env
vim .env
```

4. Install required packages.

```python
pip install -r requirements.txt
```

5. All exporters are in exporters directory. You can choose to set up cron jobs for the exporters to schedule when they should run. You can read more on how to set up a cron job here: <https://www.digitalocean.com/community/tutorials/how-to-use-cron-to-automate-tasks-ubuntu-1804>. To manually run an exporter (e.g. running the version exporter):

```bash
cd exporters
python3 version_exporter.py
```
