import yaml
import pandas as pd
from datetime import datetime, timedelta
import os

from sw import SW
from ynab import YNABClient

def setup_environment_vars():
    # Check if running in GitHub Actions
    if os.getenv('GITHUB_ACTIONS'):
        return

    # for local development
    with open('creds.yaml', 'r') as file:
        secrets = yaml.safe_load(file)
        for key, value in secrets.items():
            os.environ[key] = value

class ynab_splitwise_transfer():
    def __init__(self, sw_consumer_key, sw_consumer_secret,sw_api_key, 
                    ynab_personal_access_token, ynab_budget_name, ynab_account_name) -> None:
        self.sw = SW(sw_consumer_key, sw_consumer_secret, sw_api_key)
        self.ynab = YNABClient(ynab_personal_access_token)

        self.ynab_budget_id = self.ynab.get_budget_id(ynab_budget_name)
        self.ynab_account_id = self.ynab.get_account_id(self.ynab_budget_id, ynab_account_name)

    def sw_to_ynab_csv(self, dated_after):
        # import from splitwise
        expenses = self.sw.get_expenses(dated_after=dated_after)
        print(f"Writing {len(expenses)} expenses to csv file.")

        # convert to dataframe
        df = pd.DataFrame(expenses)
        df.rename(columns={'owed': 'Amount','date':'Date','description':'Memo'}, inplace=True)
        df['Payee'] = None
        df = df[['Date','Payee','Memo','Amount']]

        # write to a csv file
        df.to_csv("output.csv", index=False)
        print("Output file written")

    def get_YNAB_last_transaction_date(self):
        return self.ynab.get_last_transaction(self.ynab_budget_id, self.ynab_account_id)['date']
    
    def get_YNAB_last_transaction(self):
        return self.ynab.get_last_transaction(self.ynab_budget_id, self.ynab_account_id)

    def sw_to_ynab(self):
        # get last transaction date from YNAB
        last_transaction_date = self.get_YNAB_last_transaction_date()
        print(f"Last transaction on YNAB: {last_transaction_date}")
        last_transaction_date = datetime.strptime(last_transaction_date, "%Y-%m-%d")
        dated_after = last_transaction_date + timedelta(days=1)     # this date is included
        dated_before = datetime.now().date()    # this date is NOT included

        dated_after_str = dated_after.strftime('%Y-%m-%d')
        dated_before_str = dated_before.strftime('%Y-%m-%d')

        print(f"Getting transactions from {dated_after_str} to {dated_before_str} (end date not included)...")

        if dated_after_str == dated_before_str:
            print("No transactions to write to YNAB.")
            return

        # import from splitwise
        expenses = self.sw.get_expenses(dated_after=dated_after, dated_before=dated_before)

        if expenses:
            # process
            ynab_transactions = []
            for expense in expenses:
                transaction = {
                                "account_id": self.ynab_account_id,
                                "date":expense['date'],
                                "amount":-int(expense['owed']*1000),
                                "memo":expense['description'],
                                "cleared": "cleared"
                            }
                ynab_transactions.append(transaction)

            # export to ynab
            print(f"Writing {len(ynab_transactions)} record(s) to YNAB.")
            response = self.ynab.create_transaction(self.ynab_budget_id, ynab_transactions)
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
