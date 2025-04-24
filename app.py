from atproto import Client, models
import config
import requests
import time


try:
    client = Client(base_url='https://bsky.social')
    client.login(config.auth.username, config.auth.password)
except Exception as e:
    print(e)
    exit(1)


cursor = None
blocking = []

try:
    while True:
        res = client.app.bsky.graph.get_blocks({'limit': 100, 'cursor': cursor})

        blocking += [profile.did for profile in res['blocks']]
        cursor = res['cursor']

        if cursor is None:
            break
except Exception as e:
    print(e)
    exit(1)

print(f"blocking: {len(blocking)}")


clearsky_endpoint = f"https://api.clearsky.services/api/v1/anon/single-blocklist/{client.me.did}"
page = 1
blocked_by = []

try:
    while True:
        res = requests.get(f"{clearsky_endpoint}/{page}").json()
        blocklist = res['data']['blocklist']

        blocked_by += [block['did'] for block in blocklist]

        if len(blocklist) == 0:
            break
        else:
            page += 1
            time.sleep(1)
except Exception as e:
    pass

print(f"blocked_by: {len(blocked_by)}")


not_blocking = set(blocked_by) - set(blocking)
blocked_back = 0

for did in not_blocking:
    try:
        profile = client.get_profile(actor=did)

        block_record = models.AppBskyGraphBlock.Record(subject=did, created_at=client.get_current_time_iso())
        block = client.app.bsky.graph.block.create(client.me.did, block_record)
    except:
        continue
    
    print(f"blocked: {profile.handle}")

    blocked_back += 1

print(f"blocked_back: {blocked_back}")
