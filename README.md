
# Bridge

Bridge is a collection of scripts that helps you export various metrices from hosts within your local network to a cloud-based data repo.

## Why did we write Bridge?

We wrote bridge to collect and export version details of 720+ servers hosting Health Information Systems. We got a little bit carried away and started exporting more metrices other than just version details and essentially ended up with Bridge.

The exported data is visualized for stakeholders that don't have access to our local network.

## How does Bridge work?

1. We have a database of details of all hosts within our network. Thus, ip addresses, hostnames, etc. The data in this database is accessible via a simple REST API.
2. Bridge gets these host details, loop through them and collect relevant data
3. This data is then sent to a cloud-based data repo for visualization

## Installation

This section will walk you through setting up Bridge on an Ubuntu 20.04 server.

1. Clone the repo

```bash
git clone https://github.com/DoxDevOps/bridge.git
```

2. Set up a virtual environment for Bridge. You can follow instruction on how to set up a virtual environment here: <https://www.digitalocean.com/community/tutorials/how-to-install-python-3-and-set-up-a-programming-environment-on-ubuntu-20-04-quickstart>.

3. Install required packages

```bash
pip install -r requirements.txt
```

4. Provide your environment variables in the .env

```bash
mv .env.example .env
vim .env
```

5. To run bridge:

```bash
python bridge.py
```

6. All exporters are within exporter.py and are called within bridge.py. You can add more exporters to the file then simply call them within bridge.py. You can choose to set up cron jobs for the exporters to schedule when bridge should run. You can read more on how to set up a cron job here: <https://www.digitalocean.com/community/tutorials/how-to-use-cron-to-automate-tasks-ubuntu-1804>.
