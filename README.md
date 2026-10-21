# mullvadoxy
Generate foxyproxy list based on Maximko updated outputs of Mullvad proxies [proxies.txt](https://github.com/maximko/mullvad-socks-list/blob/list/socks-timezone-list.txt)

## Usage
### Everything
`python3 make_foxyproxy_list.py proxies.txt foxyproxy_all.txt --map country_names.csv`

### One region (Europe, America, Asia, Australia, Africa, Pacific)
`python3 make_foxyproxy_list.py proxies.txt foxyproxy_eu.txt --region Europe --map country_names.csv`

### Other port or scheme
`python3 make_foxyproxy_list.py proxies.txt out.txt --port 1081 --scheme socks5`
