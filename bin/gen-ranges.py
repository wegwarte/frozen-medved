import netaddr as n
import requests as r

# country two letter code
cn = 'ru'

# list of networks
nets = [n.IPNetwork(net.decode('ascii')) for net in r.get('http://www.cc2asn.com/data/%s_ipv4' % cn).iter_lines()]

for net in nets:
  print(str(n.IPAddress(net.first)) + '-' + str(n.IPAddress(net.last)))


