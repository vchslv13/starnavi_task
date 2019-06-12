import requests
from time import sleep


def verify_email(user, api_key):
    """Retrieve emai verification info.

    As the documentation (https://hunter.io/api/v2/docs#email-verifier) states:
    'The request will run for 20 seconds. If it was not able to provide
    a response in time, we will return a 202 status code. You will then
    be able to poll the same endpoint to get the verification's result.'
    Send the request as long as it doesn't return the verification results
    or the error occurs."""
    while True:
        r = requests.get('https://api.hunter.io/v2/email-verifier',
                         params={'email': user.email, 'api_key': api_key})
        if r.status_code == 200:
            res = r.json()['result']
            if res == 'deliverable':
                user.is_active = True
                user.save()
                inform_user_about_email_verification(user)
        elif r.status_code == 202:
            sleep(10)
            continue
        else:
            return  # couldn't verify email


def inform_user_about_email_verification(user):
    """Send user an email informing that his email was verified and an account
    is now active.
    """
    pass
