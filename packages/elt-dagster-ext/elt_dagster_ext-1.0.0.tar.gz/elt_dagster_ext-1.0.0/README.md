# Meltano Dagster Extention

[![PyPI version](https://badge.fury.io/py/elt-dagster-ext.svg)](https://badge.fury.io/py/elt-dagster-ext)

This project uses [`elt-dagster-meltano`](https://github.com/camisinc/elt-dagster-meltano) under the hood. Forked from the original repo that was from [Quantile Devlopment](https://github.com/quantile-development/dagster-ext); with a special thanks to [Jules Huisman](https://github.com/JulesHuisman) for the maintenance of that repo.


## Features

- Load all Meltano jobs as Dagster jobs.
- Add all correspondig schedules to these jobs.
- (todo) Load all DBT models as Dagster assets.
- (todo) Load all Singer tap streams as Dagster assets.
- (todo) Ops to perform all Meltano actions.
- (todo) Extract Singer metrics from logs and store them using Dagster.

## Installation

```sh
# Add the elt-dagster-ext to your Meltano project
meltano add utility dagster

# Initialize your Dagster project
meltano invoke dagster:initialize

# Start Dagit
meltano invoke dagster:start
```

## Commands

```sh
meltano invoke dagster:initialize
```

Setup a new Dagster project and automatically load jobs and assets from your Meltano project.

```sh
meltano invoke dagster:start
```

Start Dagit to serve your local Dagster deployment.
