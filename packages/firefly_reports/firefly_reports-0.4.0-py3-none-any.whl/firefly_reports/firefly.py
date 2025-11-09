import datetime
import re
from dataclasses import dataclass
from typing import Any, Dict, List

import requests

from .__init__ import __version__


@dataclass
class Firefly:
    url: str
    access_token: str

    def get_about(self) -> Dict[str, Any]:
        """
        Get information about the Firefly instance.
        :return: Dictionary with information about the Firefly instance.
        """
        header = {"Authorization": f"Bearer {self.access_token}"}
        about_url = f"{self.url}/api/v1/about"

        with requests.Session() as session:
            session.headers.update(header)
            about = session.get(about_url).json()["data"]

        return about

    def get_budgets(self, start_date: datetime.date, end_date: datetime.date) -> List[Dict[str, Any]]:
        header = {"Authorization": f"Bearer {self.access_token}"}
        budgets_url = f"{self.url}/api/v1/budgets?start={start_date}&end={end_date}"

        with requests.Session() as session:
            session.headers.update(header)
            budgets = session.get(budgets_url).json()["data"]

        return budgets

    def budget_report(
            self, start_date: datetime.date, end_date: datetime.date
            ) -> Dict[str, float]:

        totals = list()
        for budget in self.get_budgets(start_date=start_date, end_date=end_date):
            budget_items = budget["attributes"]
            budget_name = budget_items["name"]
            try:
                budget_spent = float(budget_items["spent"][0]["sum"])
            except:
                budget_spent = 0.1
            budget_amount = budget_items["auto_budget_amount"]
            budget_period = budget_items["auto_budget_period"]
            budget_left = float(budget_amount) + float(budget_spent)

            totals.append(
                    {
                        "name": budget_name,
                        "spent": budget_spent,
                        "remaining": budget_left,
                        "budget_period": budget_period,
                        }
                    )

        return totals

    def get_categories(self) -> List[Dict[str, Any]]:
        header = {"Authorization": f"Bearer {self.access_token}"}
        categories_url = f"{self.url}/api/v1/categories"

        with requests.Session() as session:
            session.headers.update(header)
            categories = session.get(categories_url).json()["data"]

        return categories

    def category_report(
        self, start_date: datetime.date, end_date: datetime.date
    ) -> List[Dict[str, float]]:
        header = {"Authorization": f"Bearer {self.access_token}"}
        categories_url = f"{self.url}/api/v1/categories"

        with requests.Session() as session:
            session.headers.update(header)
            totals = list()

            for category in self.get_categories():
                url = f"{categories_url}/{category['id']}?start={start_date}&end={end_date}"
                category_data = session.get(url).json()["data"]
                category_name = category_data["attributes"]["name"]
                try:
                    category_spent = category_data["attributes"]["spent"][0]["sum"]
                except (KeyError, IndexError):
                    category_spent = 0
                try:
                    category_earned = category_data["attributes"]["earned"][0]["sum"]
                except (KeyError, IndexError):
                    category_earned = 0
                category_total = float(category_spent) + float(category_earned)
                totals.append(
                    {
                        "name": category_name,
                        "spent": category_spent,
                        "earned": category_earned,
                        "total": category_total,
                    }
                )

        return totals

    def summary_report(
        self, start_date: datetime.date, end_date: datetime.date
    ) -> Dict[str, float]:
        header = {"Authorization": f"Bearer {self.access_token}"}
        summary_url = (
            f"{self.url}/api/v1/summary/basic?start={start_date}&end={end_date}"
        )

        with requests.Session() as session:
            session.headers.update(header)
            summary = session.get(summary_url).json()

        for key in summary:
            if re.match(r"spent-in-.*", key):
                currency_name = key.replace("spent-in-", "")
        spent = summary["spent-in-" + currency_name]["monetary_value"]
        earned = summary["earned-in-" + currency_name]["monetary_value"]
        net_change = summary["balance-in-" + currency_name]["monetary_value"]

        return {
            "spent": float(spent),
            "earned": float(earned),
            "net_change": float(net_change),
        }



@dataclass
class EmailReport(Firefly):
    start_date: datetime.date
    end_date: datetime.date

    def get_ordinal_suffix(self, day: int) -> str:
        if 11 <= day <= 13:
            return "th"
        else:
            suffixes = {1: "st", 2: "nd", 3: "rd"}
            return suffixes.get(day % 10, "th")

    def format_date_with_ordinal(self, date: datetime) -> str:
        day = date.day
        suffix = self.get_ordinal_suffix(day)
        return date.strftime(f"%A %B {day}{suffix}, %Y")

    def create_report(self):
        about = self.get_about()
        budgets = self.budget_report(
                start_date=self.start_date, end_date=self.end_date
                )
        categories = self.category_report(
            start_date=self.start_date, end_date=self.end_date
        )
        summary = self.summary_report(
            start_date=self.start_date, end_date=self.end_date
        )
        start_date_ytd = datetime.date(self.start_date.year, 1, 1)
        summary_ytd = self.summary_report(
            start_date=start_date_ytd, end_date=self.end_date
        )

        # Set up the categories table
        categories_table_body = (
            '<table><tr><th>Category</th><th style="text-align: right;">Total</th></tr>'
        )
        for category in categories:
            categories_table_body += (
                '<tr><td style="padding-right: 1em;">'
                + category["name"]
                + '</td><td style="text-align: right;">'
                + str(round(float(category["total"]))).replace("-", "−")
                + "</td></tr>"
            )

        categories_table_body += "</table>"

        # Set up the budget table
        budgets_table_body = (
            '<table><tr><th>Budget</th><th style="text-align: right;">Spent</th><th style="text-align: right;">Remaining</th><th style="text-align: right;">Period</th></tr>'
        )
        for budget in budgets:
            budgets_table_body += (
                '<tr><td style="padding-right: 1em;">'
                + budget["name"]
                + '</td><td style="text-align: right;">'
                + str(round(float(budget["spent"]))).replace("-", "−")
                + '</td><td style="text-align: right;">'
                + str(round(float(budget["remaining"]))).replace("-", "−")
                + '</td><td style="text-align: right;">'
                + budget["budget_period"].capitalize()
                + "</td></tr>"
                )

        budgets_table_body += "</table>"

        # Set up the general information table
        general_table_body = "<table>"
        general_table_body += (
            '<tr><td>Spent this period:</td><td style="text-align: right;">'
            + str(round(summary["spent"])).replace("-", "−")
            + "</td></tr>"
        )
        general_table_body += (
            '<tr><td>Earned this period:</td><td style="text-align: right;">'
            + str(round(summary["earned"])).replace("-", "−")
            + "</td></tr>"
        )
        general_table_body += (
            '<tr style="border-bottom: 1px solid black"><td>Net change this period:</td><td style="text-align: right;">'
            + str(round(summary["net_change"])).replace("-", "−")
            + "</td></tr>"
        )
        general_table_body += (
            '<tr><td>Spent so far this year:</td><td style="text-align: right;">'
            + str(round(summary_ytd["spent"])).replace("-", "−")
            + "</td></tr>"
        )
        general_table_body += (
            '<tr><td>Earned so far this year:</td><td style="text-align: right;">'
            + str(round(summary_ytd["earned"])).replace("-", "−")
            + "</td></tr>"
        )
        general_table_body += (
            '<tr style="border-bottom: 1px solid black"><td style="padding-right: 1em;">Net change so far this year:</td><td style="text-align: right;">'
            + str(round(summary_ytd["net_change"])).replace("-", "−")
            + "</td></tr>"
        )
        general_table_body += "</table>"

        about_body = f"""<p>Firefly version: {about["version"]}</p><p>Report version: {__version__}</p>"""

        htmlBody = f"""
                <html>
                    <head>
                        <style>table{{border-collapse: collapse; border-top: 1px solid black; border-bottom: 1px solid black;}} th {{border-bottom: 1px solid black; padding: 0.33em 1em 0.33em 1em;}} td{{padding: .1em;}} tr:nth-child(even) {{background: #EEE}} tr:nth-child(odd) {{background: #FFF}}</style>
                    </head>
                    <body>
                        <p>Report from {self.format_date_with_ordinal(self.start_date)} to {self.format_date_with_ordinal(self.end_date)}:</p>
                        {categories_table_body}
                        <p></p>
                        {budgets_table_body}
                        <p>General information:</p>
                        {general_table_body}
                        {about_body}
                    </body>
                </html>
                """

        return htmlBody
