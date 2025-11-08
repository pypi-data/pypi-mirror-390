import requests

cookies = {
    'resolution': '1920x1080',
    'interpals_sessid': 'lh0ma1dr3nfvo128m50kssrg5d',
    'csrf_cookieV2': 'rojTGpCT7xo%3D',
    '_ga': 'GA1.1.1320021298.1762499400',
    'g_state': '{"i_l":0,"i_ll":1762499400276}',
    'lt': '1446433896957296038%2Ce3eff6399561d163ae16a6505f74281fb201704bdadd8a3d217ff4f2751cf942%2C90fecb3866ae54a764e696548d1e86ce',
    'resolution': '1920x1080',
    '__gads': 'ID=b1d9ba66a66a8e20:T=1762499416:RT=1762500363:S=ALNI_MZbJVMLlhE7Q4C3wI7mVzRzOjQ_OA',
    '__gpi': 'UID=000011aff4e78231:T=1762499416:RT=1762500363:S=ALNI_MZGkth6drrdmL3Pkfl7mQSybqQong',
    '__eoi': 'ID=107a16718f039ad4:T=1762499416:RT=1762500363:S=AA-AfjbENm9PMgUzwG95BO9CMJZr',
    '__ubic1': 'SUpbJWPwuVxrDTYH',
    '_ga_0QW3XVG74P': 'GS2.1.s1762499400$o1$g1$t1762500366$j50$l0$h0',
    'FCCDCF': '%5Bnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2C%5B%5B32%2C%22%5B%5C%224d1eb8d7-acde-4fe8-af5d-36913c9e4152%5C%22%2C%5B1762499400%2C456000000%5D%5D%22%5D%5D%5D',
    'FCNEC': '%5B%5B%22AKsRol-e4Zm6w52GXSp_h-OMNLbR9PfUcWNIB7SxeSFBDEaB2FS7zCuyB5m-IcNFfMk7enWz8luL9uSvXSBLS_hzNGXUkdR5-w4_XgAZsx4_ynLdCtszHjOecusSAvsMQvccDw2RAkhozCcV7oK_g2D7BklX12Zpkg%3D%3D%22%5D%5D',
}

headers = {
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
    'accept-language': 'en-GB,en-US;q=0.9,en;q=0.8',
    'priority': 'u=0, i',
    'referer': 'https://www.interpals.net/app/profile?id=1026223282',
    'sec-ch-ua': '"Google Chrome";v="141", "Not?A_Brand";v="8", "Chromium";v="141"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
    'sec-fetch-dest': 'document',
    'sec-fetch-mode': 'navigate',
    'sec-fetch-site': 'same-origin',
    'sec-fetch-user': '?1',
    'upgrade-insecure-requests': '1',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36',
    # 'cookie': 'resolution=1920x1080; interpals_sessid=lh0ma1dr3nfvo128m50kssrg5d; csrf_cookieV2=rojTGpCT7xo%3D; _ga=GA1.1.1320021298.1762499400; g_state={"i_l":0,"i_ll":1762499400276}; lt=1446433896957296038%2Ce3eff6399561d163ae16a6505f74281fb201704bdadd8a3d217ff4f2751cf942%2C90fecb3866ae54a764e696548d1e86ce; resolution=1920x1080; __gads=ID=b1d9ba66a66a8e20:T=1762499416:RT=1762500363:S=ALNI_MZbJVMLlhE7Q4C3wI7mVzRzOjQ_OA; __gpi=UID=000011aff4e78231:T=1762499416:RT=1762500363:S=ALNI_MZGkth6drrdmL3Pkfl7mQSybqQong; __eoi=ID=107a16718f039ad4:T=1762499416:RT=1762500363:S=AA-AfjbENm9PMgUzwG95BO9CMJZr; __ubic1=SUpbJWPwuVxrDTYH; _ga_0QW3XVG74P=GS2.1.s1762499400$o1$g1$t1762500366$j50$l0$h0; FCCDCF=%5Bnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2C%5B%5B32%2C%22%5B%5C%224d1eb8d7-acde-4fe8-af5d-36913c9e4152%5C%22%2C%5B1762499400%2C456000000%5D%5D%22%5D%5D%5D; FCNEC=%5B%5B%22AKsRol-e4Zm6w52GXSp_h-OMNLbR9PfUcWNIB7SxeSFBDEaB2FS7zCuyB5m-IcNFfMk7enWz8luL9uSvXSBLS_hzNGXUkdR5-w4_XgAZsx4_ynLdCtszHjOecusSAvsMQvccDw2RAkhozCcV7oK_g2D7BklX12Zpkg%3D%3D%22%5D%5D',
}

params = {
    'uid': '1445989835698485000',
}

response = requests.get('https://www.interpals.net/app/friends/add', params=params, cookies=cookies, headers=headers)
print(response.text)