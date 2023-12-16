import os
import yaml

def setup_environment_vars():
    # Check if running in GitHub Actions
    if os.getenv('GITHUB_ACTIONS'):
        return

    # for local development
    with open('creds.yaml', 'r') as file:
        secrets = yaml.safe_load(file)
        for key, value in secrets.items():
            os.environ[key] = value

def combine_names(string_list):
    if not string_list:
        return ""

    if len(string_list) == 1:
        return string_list[0]

    return ', '.join(string_list[:-1]) + ' and ' + string_list[-1]