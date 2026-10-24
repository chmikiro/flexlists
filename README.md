# flexlists, what is?
Generate proxies list (only foxyproxy currently) based on daily updated local socks5 addresses for [Mullvad](https://mullvad.net/en/help/socks5-proxy) proxying layer: [**`proxies.txt`**](https://github.com/maximko/mullvad-socks-list/blob/list/socks-timezone-list.txt)

The script simply converts "ip timezone" dataset to Foxyproxy [extended import lines](https://github.com/foxyproxy/firefox-extension/wiki/Import-Proxy-List): `protocol://username:password@server:port?parameter1=value1&parameter2=value2`

Country/ISO code come from the system tz database (zone.tab + iso3166.tab). Optional --map CSV overrides/extends it.

> This script can virtually be adapted to any output format quite efficiently, feel free to contribute.


## Usage
### Everything
`python3 make_foxyproxy_list.py proxies.txt foxyproxy_all.txt --map country_names.csv`


### One region (Europe, America, Asia, Australia, Africa, Pacific)
`python3 make_foxyproxy_list.py proxies.txt foxyproxy_eu.txt --region Europe --map country_names.csv`


### Other port or scheme
`python3 make_foxyproxy_list.py proxies.txt out.txt --port 1081 --scheme socks5`


# Aknowledgements
- [**Maximko**](https://github.com/maximko)
