# Firefly Reports

Generate email reports using [Firefly's API](https://api-docs.firefly-iii.org).
There is a [wiki](https://github.com/cetyler/firefly_reports/wiki) which will
have more information.

## Firefly

[Firefly](https://www.firefly-iii.org) is a free and open source personal
finance manager.
Firefly Reports adds the ability to get email reports to help keep track of
your spending.

## Quickstart

To install, you can use `pipx`:

```bash
$ pipx install firefly_reports
```

or use `uv`:

```bash
$ uv tool install firefly_reports
```

If using `pip`, I would suggest using a virtual environment.
After installing, you can use `--help` to get the inputs:

```bash
Usage: firefly_reports [OPTIONS] CONFIG_FILE

Options:
  --start_date [%Y-%m-%d]
  --end_date [%Y-%m-%d]
  --help                   Show this message and exit.
```

By default the start date will be a week from when the program is run and the
end date will be the day of the program is run.

Copy [example_config.toml](https://github.com/cetyler/firefly_reports/blob/main/example_config.toml)
to your PC and update the following:

```toml
[email]
server = "smtp.gmail.com"
port = 587
starttls = true         # Use STARTTLS
authentication = true   # Login with username and password
user = "your_email_address@gmail.com"
password = "password"
from = "your_email_address@gmail.com"
to = ["email1@example.com","email2@example.com"]

[firefly]
url = "http://firefly_instance:8085"
access_token = "your_api_access_token_key"
```

I verified that using [Gmail](https://gmail.com) works but haven't checked other email
providers.
Look at [Firefly's documentation](https://docs.firefly-iii.org/how-to/firefly-iii/features/api/)
to get your access token.

## Reports

Currently only one report is supported.
This report will include the following:

- Categories (income and expenses).
- Total amount spent between the start and end dates.
- Total amount earned between the start and end dates.
- Total amount spent so far for the calendar year.
- Total amount earned so far for the calendar year.

## Development

The recommended way is to use `uv`:

```bash
$ git clone git@github.com:cetyler/firefly_reports.git
$ uv venv --python 3.13
Using Python 3.13
Creating virtualenv at: .venv
Activate with: source .venv/bin/activate
$ source .venv/bin/activate
$ uv sync --dev
```