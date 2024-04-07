# splitwise_ynab_sync

## What does it do?
The code automates the process of importing transactions from Splitwise into your YNAB budget.By following instructions below, you can automate to run it daily using Github Actions. So, your Splitwise transactions will be imported everyday just like your other automated accounts.

## What change do you need in your YNAB workflow to implement this?
You would need to create a new account named 'Splitwise' in your YNAB accounts(mentioned below in Setup #1).
That is the only necessity for this repo.

That said, I would to mention my workflow:
- In addition to a 'Splitwise' account, I also create a 'Splitwise' category. I place this in a 'Don't count' group as it helps in the reports.
- Expenses paid by me: I split the expense between a category corrsponding to the expense and the 'Splitwise' category.
- Expenses paid by others: I add my share as an expense under 'Splitwise' account and the corresponding category.

## Which transactions are imported?
The code imports all the **transactions for which you owe money**.

## Is it free?
Yes. Since you will be deploying your own Github Actions to deploy, you will be using just around 15 minutes from the [free 2000 minutes per month](https://docs.github.com/en/billing/managing-billing-for-github-actions/about-billing-for-github-actions#included-storage-and-minutes).

## Setup
This repo moves transactions from Splitwise to YNAB.

1. Go to your YNAB budget ([YNAB](https://app.youneedabudget.com/)) and create a new account named `Splitwise`. This is where the imported transactions will flow into.
2. Collect Credentials from YNAB and Splitwise:

    a. YNAB:
     - Go to [YNAB Developer Settings](https://app.ynab.com/settings/developer)
     - Create a new `Personal Access Token`.
     - You will see the token at the top of page, save that in a safe place as you won't be able to access it again.
    
    b. Splitwise:
    - Go to [Splitwise Apps](https://secure.splitwise.com/apps)
    - Click on `Register your application`
    - Fill `application name` (YNAB_Splitwise_sync), `description` and `Homepage URL` (http://api-example.splitwise.com/) and click on `Register and API key`
    - Copy `Consumer Key`, `Consumer Secret` and `API keys`.
3. Fork this repo. (by clicking on the 'Fork' option on the top of this page.)
4. Add the Credentials on Github Actions:
    - Go to the `Settings` tab, then `Secrets and variables` > `Actions`
    - Under `Secrets` tab, using `New repository secret`, you need to add 4 Name-Secret pairs:
        - Name: `YNAB_PERSONAL_ACCESS_TOKEN`, Secret: `Personal Access Token` from 2a.
        - Name: `SW_API_KEY`, Secret: `API keys` from 2b.
        - Name: `SW_CONSUMER_KEY`, Secret: `Consumer Key` from 2b.
        - Name: `SW_CONSUMER_SECRET`, Secret: `Consumer Secret` from 2b.
    - Similarly, Under `Variables` tab, using `New repository variable`, add:
        - Name: `YNAB_BUDGET_NAME`, Value: your YNAB budget name (check your YNAB app or website, if you don't know, fill 'My Budget')
        - Name: `YNAB_ACCOUNT_NAME`, Value: 'Splitwise' (created in step 1).


The Github Actions now triggers this code repo at `12:00 UTC` everyday and transfers previous day's transactions from Splitwise to YNAB.

If you would like to change the schedule time, change the cron expression in [python-app.yaml](.github/workflows/python-app.yml) file.


## Bugfixes
1. Apr 6, 2024: fixed the `UnboundLocalError: local variable 'paid' referenced before assignment` error.

### How to keep your repo updated to this repo?
1. On your forked repo, you would see something like `This branch is X commits behind amit-hm/splitwise_yanb_sync:main`.
2. Click on `Sync fork`.
3. Click on `Update branch`.
   This should update your forked repo to this repo and hence bring in those new bugfixes or features.

# NOTE
Github Actions, unfortunately, deactivates after 60 days of inactivity. So, you might have to manually enable the workflow again every 60 days.


Contact me at devsama42@gmail.com
