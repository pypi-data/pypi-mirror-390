import datetime

import click

from .config import get_config
from .email import Email
from .firefly import EmailReport


@click.command()
@click.argument("config_file", type=click.Path(exists=True))
@click.option(
    "--start_date",
    default=f"{datetime.date.today() - datetime.timedelta(days=7)}",
    type=click.DateTime(formats=["%Y-%m-%d"]),
)
@click.option(
    "--end_date",
    default=f"{datetime.date.today()}",
    type=click.DateTime(formats=["%Y-%m-%d"]),
)
def main(config_file, start_date, end_date):
    config = get_config(config_file)

    report = EmailReport(
        url=config["firefly"]["url"],
        access_token=config["firefly"]["access_token"],
        start_date=start_date,
        end_date=end_date,
    )

    email_report = report.create_report()

    email_message = Email(
        email_to=config["email"]["to"],
        email_from=config["email"]["from"],
        subject=f"Firefly Report {start_date.date()} to {end_date.date()}",
        body=email_report,
        smtp_server=config["email"]["server"],
        smtp_port=config["email"]["port"],
        smtp_starttls=config["email"]["starttls"],
        smtp_user=config["email"]["user"],
        smtp_password=config["email"]["password"],
        smtp_authentication=config["email"]["authentication"],
    )

    email_message.send_email()


if __name__ == "__main__":
    main()
