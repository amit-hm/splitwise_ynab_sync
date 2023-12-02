import pandas as pd
from datetime import datetime, timedelta
import os

from sw import SW
from ynab import YNABClient
from utils import setup_environment_vars
from datetime import datetime, timezone

class ynab_splitwise_transfer():
    def __init__(self, sw_consumer_key, sw_consumer_secret,sw_api_key, 
                    ynab_personal_access_token, ynab_budget_name, ynab_account_name) -> None:
        self.sw = SW(sw_consumer_key, sw_consumer_secret, sw_api_key)
        self.ynab = YNABClient(ynab_personal_access_token)

        self.ynab_budget_id = self.ynab.get_budget_id(ynab_budget_name)
        self.ynab_account_id = self.ynab.get_account_id(self.ynab_budget_id, ynab_account_name)

    def sw_to_ynab(self):
        now = datetime.now(timezone.utc)
        todays_midnight = datetime(now.year, now.month, now.day)
        yesterdays_midnight = todays_midnight - timedelta(days=1)

        expenses = self.sw.get_expenses(dated_after=yesterdays_midnight, dated_before=todays_midnight)

        if expenses:
            # process
            ynab_transactions = []
            for expense in expenses:
                # don't import deleted expenses
                if expense['deleted_time']:
                    continue
                transaction = {
                                "account_id": self.ynab_account_id,
                                "date":expense['date'],
                                "amount":-int(expense['owed']*1000),
                                "memo":expense['description'],  # add other users
                                "cleared": "cleared"
                            }
                ynab_transactions.append(transaction)
            # export to ynab
            if ynab_transactions:
                print(f"Writing {len(ynab_transactions)} record(s) to YNAB.")
                response = self.ynab.create_transaction(self.ynab_budget_id, ynab_transactions)
            else:
                print("No transactions to write to YNAB.")
        else:
            print("No transactions to write to YNAB.")


if __name__=="__main__":
    # load environment variables from yaml file (locally)
    setup_environment_vars()

    # splitwise creds
    sw_consumer_key = os.environ.get('sw_consumer_key')
    sw_consumer_secret = os.environ.get('sw_consumer_secret')
    sw_api_key = os.environ.get('sw_api_key')

    # ynab creds
    ynab_budget_name = os.environ.get('ynab_budget_name')
    ynab_account_name = os.environ.get('ynab_account_name')
    ynab_personal_access_token = os.environ.get('ynab_personal_access_token')

    a = ynab_splitwise_transfer(sw_consumer_key, sw_consumer_secret,
                                sw_api_key, ynab_personal_access_token,
                                ynab_budget_name, ynab_account_name)

    # splitwise to ynab
    a.sw_to_ynab()
