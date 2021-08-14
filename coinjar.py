from urllib3.exceptions import InsecureRequestWarning
import twocaptcha
import json
import requests


requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)

def get_auth_token(data):
    return data.split(
            '<input type="hidden" name="authenticity_token" value="'
            )[1].split('"')[0]


def is_registered(email, solver, config):
    auth_token = get_auth_token(
            requests.get("https://secure.coinjar.com/users/sign_up").text
            )
    recaptcha = solver.recaptcha(
            sitekey=config['coinjar']['sitekey'],
            url="https://secure.coinjar.com/users"
            )['code']
    res = requests.post("https://secure.coinjar.com/users", data={
        "authenticity_token": auth_token,
        "user[first_name]": "John",
        "user[last_name]": "Doe",
        "user[email]": email,
        "user[password]": "StrongPassword1@3",
        "user[password_confirmation]": "StrongPassword1@3",
        "user[terms_of_service]": 1,
        "user[list_subscription]": 0,
        "g-recaptcha-response": recaptcha,
        "recaptcha_v2_token": recaptcha
        }, verify=False)
    return "Email has already been taken" in res.text


if __name__ == "__main__":
    with open("recaptcha_config.json") as config:
        config = json.load(config)
    solver = twocaptcha.TwoCaptcha(config['twocaptcha']['apikey'])
    res = is_registered(
            (email := input("Email: ")), solver, config
            )
    print(f"{email!r} is{'' if res else ' not'} registered")
