import aiohttp
import asyncio
import json


def get_input_value(data, name):
    return data.split(
            f"<input type=\"hidden\" id=\"{name}\" name=\"{name}\" value=\""
            )[1].split("\"")[0]


def get_proof_methods(data):
    proof_methods = data.split("proofList\":")[1]
    n = 1
    while True:
        try:
            return json.loads(proof_methods.split("}]", n)[0] + "}]")
        except Exception as exc:
            n += 1


def get_uaid(data):
    return data.split("uaid=")[1].split("\"")[0]


async def get_password_reset_info(email):
    async with aiohttp.ClientSession(
            connector=aiohttp.TCPConnector(verify_ssl=False)
            ) as session:
        async with session.get(
                "https://account.live.com/ResetPassword.aspx"
                ) as response:
            while True:
                try:
                    data = await response.text()
                    break
                except asyncio.exceptions.TimeoutError:
                    print("retrying due to timeout")
            prepared_form_data = {
                    name: get_input_value(data, name)
                    for name in (
                        "iAction", "iRU", "amtcxt", "isSigninNamePhone",
                        "canary"
                        )
                    }
            prepared_form_data.update({
                "iSigninName": email
                })
            uaid = get_uaid(data)
        async with session.post(
                f"https://account.live.com/password/reset?uaid={uaid}",
                data=prepared_form_data
                ) as response:
            while True:
                try:
                    data = await response.text()
                    break
                except asyncio.exceptions.TimeoutError:
                    print("retrying due to timeout")
            if "proofList" not in data:
                print("possibly invalid email, ", end="", flush=True)
                return
            for method in get_proof_methods(data):
                if method['type'] == "Sms":
                    return method['name']
            else:
                print("this account doesn't support SMS, ", end="", flush=True)


async def main(email):
    print(await get_password_reset_info(email))


if __name__ == "__main__":
    asyncio.get_event_loop().run_until_complete(main(
        input("Email: ")
        ))
