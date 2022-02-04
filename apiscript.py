import requests, json

payload =  {
    'cmd': 'getVariables',
    'requestId':'63a35aa3-4b49-4ed4-810c-f8f0bcca724c', 
    'apiSecToken':'gVD1ev4zoGjw8wUVK1Ps9sBM3qzI3ys2nHj27XTG58JbrUYE',
    'campaignId':'udsregression',
    'hostName':'nightingale514.ushur.dev',
    'enterpriseId':'udsregressiondummy',
    }

r = requests.post(f"https://{payload['hostName']}/infoQuery", data=payload)
print(r)
