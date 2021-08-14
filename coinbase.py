import cloudscraper
import twocaptcha
import json


def is_registered(email, solver, config):
    recaptcha = solver.recaptcha(
            sitekey=config['coinbase']['sitekey'],
            url="https://www.coinbase.com/signup",
            enterprise=True, version='v3'
            )['code']
    sess = cloudscraper.create_scraper(captcha={
        "provider": "2captcha",
        "api_key": config['twocaptcha']['apikey']
        })
    res = sess.post("https://www.coinbase.com/api/v2/web/users", headers={
        "recaptcha-token": recaptcha,
        "x-cb-pagekey": "signup",
        "x-cb-platform": "web"
        }, json={
            "accepted_privacy_notice": True,
            "consent_information": [{
                "region": "EU",
                "values": ["NECESSARY", "PERFORMANCE", "FUNCTIONAL",
                           "TARGETING"]
                }],
            "email": email,
            "email_preference": {"should_send_marketing": False},
            "first_name": "John",
            "last_name": "Doe",
            "locale": "en",
            "password": "StrongPassword1@3",
            "state": "",
            "threatmetrix_session_id": ""
            }).json()
    for err in res.get("errors", []):
        if err['id'] == "user_exists":
            return True
    return False


if __name__ == "__main__":
    with open("recaptcha_config.json") as config:
        config = json.load(config)
    solver = twocaptcha.TwoCaptcha(config['twocaptcha']['apikey'])
    res = is_registered((email := input("Email: ")), solver, config)
    print(f"{email!r} is{'' if res else ' not'} registered")
