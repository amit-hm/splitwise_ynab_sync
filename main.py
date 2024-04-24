import os
import logging
from datetime import datetime, timedelta, timezone

from sw import SW
from ynab import YNABClient
from utils import setup_environment_vars, combine_names

class ynab_splitwise_transfer():
    def __init__(self, sw_consumer_key, sw_consumer_secret,sw_api_key, 
                    ynab_personal_access_token, ynab_budget_name, ynab_account_name) -> None:
        self.sw = SW(sw_consumer_key, sw_consumer_secret, sw_api_key)
        self.ynab = YNABClient(ynab_personal_access_token)

        self.ynab_budget_id = self.ynab.get_budget_id(ynab_budget_name)
        self.ynab_account_id = self.ynab.get_account_id(self.ynab_budget_id, ynab_account_name)

        logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
        self.logger = logging.getLogger(__name__)

        # timestamps
        now = datetime.now(timezone.utc)
        self.end_date = datetime(now.year, now.month, now.day)
        self.sw_start_date = self.end_date - timedelta(days=1)
        self.ynab_start_date = self.end_date - timedelta(days=3)

    def sw_to_ynab(self):
        self.logger.info("Moving transactions from Splitwise to YNAB...")
        self.logger.info(f"Getting all Splitwise expenses from {self.sw_start_date} to {self.end_date}")
        expenses = self.sw.get_expenses(dated_after=self.sw_start_date, dated_before=self.end_date)

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
                                "memo":" ".join([expense['description'].strip() ,"with", combine_names(expense['users'])]),
                                "cleared": "cleared"
                            }
                ynab_transactions.append(transaction)
            # export to ynab
            if ynab_transactions:
                self.logger.info(f"Writing {len(ynab_transactions)} record(s) to YNAB.")
                response = self.ynab.create_transaction(self.ynab_budget_id, ynab_transactions)
            else:
                self.logger.info("No transactions to write to YNAB.")
        else:
            self.logger.info("No transactions to write to YNAB.")

    def ynab_to_sw(self):
        def extract_names(s):
            s = s.replace('and', ',').replace(' ', '')
            names = s.split(',')
            return names
        
        def update_ynab(transaction, friends):
            amount = transaction['amount']
            category1_id = transaction['category_id']       # category already classified by the user
            category1_amount = amount/(len(friends) + 1) * 100

            category2_id = self.ynab.get_category_id(self.ynab_budget_id, "Splitwise")      # Splitwise catgeory
            category2_amount = (amount * 100 - category1_amount)
            transaction['subtransactions'] = [
                        {
                            'amount': round(category1_amount/100),
                            'category_id': category1_id
                        },
                        {
                            'amount': round(category2_amount/100),
                            'category_id': category2_id
                        }
                    ]
            transaction['memo'] = "Added to " + transaction['memo']
            update_transaction = {'transaction': transaction}
            self.ynab.update_transaction(self.ynab_budget_id, transaction['id'], update_transaction)
        
        def update_splitwise(transaction_friends, amount):
            category1_amount = amount/(len(transaction_friends) + 1) * 100
            expense_friends_ids = []
            sw_friends, sw_friends_ids = self.sw.get_friends()      # get all friends list from Splitwise
            for friend in transaction_friends:
                for sw_friend, friend_id in zip(sw_friends, sw_friends_ids):
                    if friend.lower() in sw_friend.lower():
                        expense_friends_ids.append(friend_id)

            total_amount = -amount/1000
            expense = {
                    'cost': total_amount,
                    'date': transaction['date'],
                    'description': transaction['payee_name'],
                    'users': []
            }
            # add current user
            current_user_owed = -round(category1_amount/100000,2)
            current_user_expense = {
                    'id': self.sw.current_user_id,
                    'owed': current_user_owed,
                    'paid': total_amount
                    }
            expense['users'].append(current_user_expense)
            
            # add friends
            total_friends_share = 0
            for i, friend_id in enumerate(expense_friends_ids):
                if i == len(expense_friends_ids) -1:
                    friends_share = total_amount - total_friends_share - current_user_owed
                else:
                    friends_share = round((total_amount - current_user_owed)/len(expense_friends_ids),2)
                total_friends_share += friends_share
                user_expense = {
                    'id': friend_id,
                    'owed': friends_share,
                    'paid': 0
                    }
                expense['users'].append(user_expense)

            expense, error = self.sw.create_expense(expense)
            return expense, error

        self.logger.info("Moving transactions from YNAB to Splitwise...")
        # get all accounts linked
        accounts = self.ynab.get_accounts(self.ynab_budget_id)
        
        for account in accounts['data']['accounts']:
            account_id = self.ynab.get_account_id(self.ynab_budget_id, account['name'])
            # get all transactions in last one day
            self.logger.info(f"Getting all YNAB transactions from {self.ynab_start_date} to {self.end_date}")
            response = self.ynab.get_transactions(self.ynab_budget_id, account_id, 
                                                        since_date=self.ynab_start_date, 
                                                        before_date=self.end_date)
            for transaction in response['data']['transactions']:
                # check the memo for 'splitwise' keyword
                if not transaction['memo']:
                    continue
                memo = transaction['memo'].lower()
                if 'splitwise' in memo and not 'added to splitwise' in memo:
                    transaction_friends = transaction['memo'].split('with')[1].strip()
                    transaction_friends = extract_names(transaction_friends)
                    
                    # update Splitwise
                    expense, error = update_splitwise(transaction_friends, transaction['amount'])

                    # update YNAB
                    if expense and not error:
                        self.logger.info("Added a transaction on Splitwise")
                        update_ynab(transaction, transaction_friends)
                        self.logger.info("Updated YNAB transaction")
                    

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
    a.ynab_to_sw()
