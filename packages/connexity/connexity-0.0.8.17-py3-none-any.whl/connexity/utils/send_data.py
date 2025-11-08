from connexity.CONST import CONNEXITY_URL
from uuid import UUID
import aiohttp

def convert_uuids(obj):
    if isinstance(obj, UUID):
        return str(obj)
    elif isinstance(obj, dict):
        return {k: convert_uuids(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [convert_uuids(item) for item in obj]
    return obj

async def send_data(answer_dict, api_key, url=CONNEXITY_URL):
    print('CONNEXITY SDK DEBUG| CALL COLLECTED DATA:', flush=True)
    print(answer_dict, flush=True)
    answer_dict = convert_uuids(answer_dict)
    async with aiohttp.ClientSession() as session:
        async with session.post(url, headers={"X-API-KEY": api_key}, json=answer_dict) as response:
            if response.status != 200:
                print(
                    f"Coonexity SDK: Failed to send data: {response.status}", flush=True)
                print(response, flush=True)
            else:
                print(
                    f"Coonexity SDK: Data sent successfully: {response.status}", flush=True)
