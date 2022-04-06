# Bridge

Bridge is a collection of scripts that help you export various metrices of remote hosts to a central data repo.

## Why we wrote Bridge?

We manage over ~800 remote hosts running Electronic Medical Record Systems (EMRS) somewhere in Africa! Each EMRS site is independent - with some sites connected to a central hub over an intermittent VPN connection. We wrote bridge to collect EMRS version data for connected sites. And got a little bit carried away and started exporting more metrices.

## Alternatives

Depending on your environment, you can use better monitoring systems (like Prometheus).

## Installation

This section will walk you through setting up Bridge on an Ubuntu 20.04 server.

1. Set up a virtual environment for Bridge (You can follow instruction on how to set up a virtual environment here: <https://www.digitalocean.com/community/tutorials/how-to-install-python-3-and-set-up-a-programming-environment-on-ubuntu-20-04-quickstart>)

2. Install required packages

3. Set up cron jobs for the exporters
