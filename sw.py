from splitwise import Splitwise
from splitwise.expense import Expense
from splitwise.user import ExpenseUser
import os
from utils import setup_environment_vars

# https://github.com/namaggarwal/splitwise

class SW():
    def __init__(self, consumer_key, consumer_secret, api_key) -> None:
        # Initialize the Splitwise object with the API key
        self.sw = Splitwise(consumer_key, consumer_secret, api_key=api_key)

        self.limit = 100
        self.current_user = self.sw.getCurrentUser().getFirstName()
        self.current_user_id = self.sw.getCurrentUser().getId()

    def get_friends(self):
        friends_fullnames = []
        friends_ids = []
        for friend in self.sw.getFriends():
            id = friend.getId()
            full_name = friend.getFirstName()
            if friend.getLastName() is not None:
                full_name = " ".join([full_name, friend.getLastName()])
            friends_fullnames.append(full_name)
            friends_ids.append(id)
        return friends_fullnames, friends_ids

    def get_expenses(self, updated_before=None, updated_after=None):
        # get all expenses between 2 dates
        expenses = self.sw.getExpenses(limit=self.limit, 
                                       updated_before=updated_before, 
                                       updated_after=updated_after)
        owed_expenses = []
        for expense in expenses:
            owed_expense = {}
            users = expense.getUsers()
            user_names = []
            expense_cost = float(expense.getCost())
            is_append = False

            for user in users:
                user_first_name = user.getFirstName()
                if user_first_name == self.current_user:
                    paid = float(user.getPaidShare())
                    description = expense.getDescription()
                    if paid == 0 and description.strip() != 'Payment':
                        owed_expense['owed'] = float(user.getOwedShare())
                        owed_expense['date'] = expense.getDate()
                        owed_expense['created_time'] = expense.getCreatedAt()
                        owed_expense['updated_time'] = expense.getUpdatedAt()
                        owed_expense['deleted_time'] = expense.getDeletedAt()
                        owed_expense['description'] = description
                        owed_expense['cost'] = expense_cost
                        is_append = True
                else:       # get user names other than current_user
                    paid_share = float(user.getPaidShare())
                    if paid_share == expense_cost:
                        user_names.append("[" + user_first_name + "]")
                    else:
                        user_names.append(user_first_name)
            if is_append:      # check category instead of description
                owed_expense['users'] = user_names
                owed_expenses.append(owed_expense)
        return owed_expenses
    
    def create_expense(self, expense):
        e = Expense()
        e.setCost(expense['cost'])
        e.setDate(expense['date'])
        e.setDescription(expense['description'])

        users = []
        for user in expense['users']:
            u = ExpenseUser()
            u.setId(user['id'])
            u.setPaidShare(user['paid'])
            u.setOwedShare(user['owed'])

            users.append(u)

        e.setUsers(users)
        expense, errors = self.sw.createExpense(e)
        if errors:
            print(errors.getErrors())
        return expense, errors


if __name__ == "__main__":
    # load environment variables from yaml file (locally)
    setup_environment_vars()
    
    # splitwise creds
    consumer_key = os.environ.get('sw_consumer_key')
    consumer_secret = os.environ.get('sw_consumer_secret')
    api_key = os.environ.get('sw_api_key')

    a = SW(consumer_key, consumer_secret, api_key)
    # e = a.get_expenses(dated_after="2023-11-29", dated_before="2023-12-01")
    
    a.create_expense()
    # a.get_friends()
