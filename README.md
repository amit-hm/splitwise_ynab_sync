# splitwise_ynab_sync

This repo moves transactions from Splitwise to YNAB.

1. Go to [YNAB](https://app.youneedabudget.com/) and create a new account named `Splitwise`.
2. Collect Credentials from YNAB and Splitwise:

    YNAB:
     - Go to [YNAB Developer Settings](https://app.ynab.com/settings/developer)
     - Create a new `Personal Access Token`.
     - Save that in a safe place as you won't be able to access it again.
    
    Splitwise:
    - Go to [Splitwise Apps](https://secure.splitwise.com/apps)
    - Click on `Register your application`
    - Fill `application name` (YNAB_Splitwise_sync), `description` and `Homepage URL` (http://api-example.splitwise.com/) and click on `Register and API key`
    - Copy `Consumer Key`, `Consumer Secret` and `API keys`.
3. Fork this repo.
4. Add the Credentials on Github Actions:
    - Go to the `Settings` tab, then `Secrets and variables` > `Actions`
    - Under `Secrets` tab, using `New repository secret`, add `SW_API_KEY`, `SW_CONSUMER_KEY`, `SW_CONSUMER_SECRET` and `YNAB_PERSONAL_ACCESS_TOKEN` (collected in step 1).
    - Under `Variables` tab, using `New repository variable`, add `YNAB_BUDGET_NAME` (your YNAB budget name) and `YNAB_ACCOUNT_NAME` (created in step 1).


The Github Actions now triggers this code repo at `00:00 UTC` everyday and transfers transactions from Splitwise to YNAB.

If you would like to change the schedule time, change the cron expression in [python-app.yaml](.github/workflows/python-app.yml) file.