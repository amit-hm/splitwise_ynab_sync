# splitwise_ynab_sync

This repo moves transactions from Splitwise to YNAB.

1. Collect Credentials from YNAB and Splitwise:

    YNAB:
     - Go to <a href="https://app.ynab.com/settings/developer" target="_blank">YNAB Developer Settings</a>
     - Create a new `Personal Access Token`.
     - Save that in a safe place as you won't be able to access it again.
    
    Splitwise:
    - Go to <a href="https://secure.splitwise.com/apps" target="_blank">Splitwise Apps</a>
    - Click on `Register your application`
    - Fill `application name` (YNAB_Splitwise_sync), `description` and `Homepage URL` (http://api-example.splitwise.com/) and click on `Register and API key`
    - Copy `Consumer Key`, `Consumer Secret` and `API keys`.
2. Fork this repo.
3. Add the Credentials on Github Actions:
    - Go to the `Settings` tab, then `Secrets and variables` > `Actions`
    - Under `Secrets` tab, using `New repository secret`, add `SW_API_KEY`, `SW_CONSUMER_KEY`, `SW_CONSUMER_SECRET` and `YNAB_PERSONAL_ACCESS_TOKEN` (collected in step 1).
    - Under `Variables` tab, using `New repository variable`, add `YNAB_BUDGET_NAME` (your YNAB budget name) and `YNAB_ACCOUNT_NAME` (create an account on YNAB named `Splitwise` or some other name).


The Github Actions now triggers this code repo at `00:00 UTC` everyday and transfers transactions from Splitwise to YNAB.

If you would like to change the schedule time, change the cron expression in <a href="https://github.com/amit-hm/splitwise_ynab_sync/blob/main/.github/workflows/python-app.yml" target="_blank">python-app.yaml</a> file.