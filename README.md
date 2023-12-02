# splitwise_ynab_sync

## What does it do?
The code automates the process of importing transactions from Splitwise into your YNAB budget.By following instructions below, you can automate to run it daily using Github Actions. So, your Splitwise transactions will be imported everyday just like your other automated accounts.

## Which transactions are imported?
The code imports all the **transactions for which you owe money**.

Note: By design, there is one delay in importing transactions i.e. if you run the code today, it will get all transactions through yesterday and not today. This is because YNAB does not have timestamp information with their dates.

## Is it free?
Yes. Since you will be deploying your own Github Actions to deploy, you will be using from [free 2000 minutes per month](https://docs.github.com/en/billing/managing-billing-for-github-actions/about-billing-for-github-actions).

## Setup
This repo moves transactions from Splitwise to YNAB.

1. Go to your YNAB budget ([YNAB](https://app.youneedabudget.com/)) and create a new account named `Splitwise`. This is where the imported transactions will flow into.
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


The Github Actions now triggers this code repo at `12:00 UTC` everyday and transfers previous day's transactions from Splitwise to YNAB.

If you would like to change the schedule time, change the cron expression in [python-app.yaml](.github/workflows/python-app.yml) file.
