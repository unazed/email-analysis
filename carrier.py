import aiohttp
import asyncio
import json


class CarrierPool:
    def __init__(self, auth_map):
        self.auth_map = auth_map
    
    async def get_carriers(self, number):
        results = {}
        async with aiohttp.ClientSession(
                connector=aiohttp.TCPConnector(verify_ssl=False)
                ) as session:
            for carrier in self.auth_map['carriers']:
                if (carrier_fn := getattr(self, f"carrier_{carrier}", None)) \
                        is None:
                    print(f"error: {carrier!r} unimplemented, skipping...")
                    continue
                while True:
                    try:
                        results[carrier] = await carrier_fn(
                                number, session,
                                **self.auth_map['carriers'][carrier]
                                ) or None
                        break
                    except (aiohttp.client_exceptions.ContentTypeError,
                            asyncio.exceptions.TimeoutError):
                        print("retrying due to ratelimiting/timeout")
                        await asyncio.sleep(5)
        return results

    async def carrier_numverify(self, number, session, key):
        async with session.get(
                f"http://apilayer.net/api/validate?access_key={key}&number="
                f"{number}"
                ) as response:
            return (await response.json()).get('carrier')

    async def carrier_twilio(self, number, session, sid, auth):
        async with session.get(
                f"https://lookups.twilio.com/v1/PhoneNumbers/{number}"
                 "?Type=carrier",
                auth=aiohttp.BasicAuth(sid, auth)
                ) as response:
            return (await response.json()).get("carrier", {}).get("name")

    async def carrier_telnyx(self, number, session):
        async with session.get(
                f"https://api.telnyx.com/anonymous/v2/number_lookup/{number}"
                ) as response:
            return (await response.json()).get('data', {})\
                    .get('carrier', {}).get('name')


async def main(number):
    with open("carrier_authentication.json") as auth:
        pool = CarrierPool(json.load(auth))
    print(await pool.get_carriers(number))


if __name__ == "__main__":
    asyncio.get_event_loop().run_until_complete(main(
        input("Number: ")
        ))
