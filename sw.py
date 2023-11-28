from splitwise import Splitwise
import yaml

# https://github.com/namaggarwal/splitwise

class SW():
    def __init__(self, consumer_key, consumer_secret, api_key) -> None:
        # Initialize the Splitwise object with the API key
        self.sw = Splitwise(consumer_key, consumer_secret, api_key=api_key)

        self.limit = 100
        self.current_user = self.sw.getCurrentUser().getFirstName()
        print("Current User: ", self.current_user)

    def get_expenses(self, dated_before=None, dated_after=None):
        # get all expenses between 2 dates
        expenses = self.sw.getExpenses(limit=self.limit, dated_before=dated_before, dated_after=dated_after)
        owed_expenses = []
        for expense in expenses:
            owed_expense = {}
            users = expense.getUsers()
            user_names = []

            for user in users:
                user_first_name = user.getFirstName()
                if user_first_name == self.current_user:
                    paid = float(user.getPaidShare())
                    description = expense.getDescription()
                    if paid == 0 and description.strip() != 'Payment':
                        owed_expense['owed'] = float(user.getOwedShare())
                        owed_expense['date'] = expense.getDate()
                        owed_expense['description'] = description
                        owed_expense['cost'] = float(expense.getCost())
                else:
                    user_names.append(user_first_name)      # get user names other than current_user
            if paid == 0 and description.strip() != 'Payment':      # check category instead of description
                owed_expense['users'] = user_names
                owed_expenses.append(owed_expense)
        return owed_expenses


if __name__ == "__main__":
    # read creds file
    with open("creds.yaml", 'r') as stream:
        try:
            data = yaml.safe_load(stream)
        except yaml.YAMLError as exc:
            print(exc)
    
    # splitwise creds
    consumer_key = data['splitwise']['consumer_key']
    consumer_secret = data['splitwise']['consumer_secret']
    api_key = data['splitwise']['api_key']

    a = SW(consumer_key, consumer_secret, api_key)
    e = a.get_expenses(dated_after="2023-11-10")
    print(e)
