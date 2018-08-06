
#code{{data['response']['code']}}
server = self._host['data']['response']['headers'].get('Server', None)
{% if server != none %}


" Server: #%s\n" % server

else:

"\n"

if self._host['data']['title']:

"Title: %s\n" % self._host['data']['title']

"Geo: %s/%s\n" % (self._host['data']['geo']['country'], self._host['data']['geo']['city'])
"http://%s:%s/\n" % (self._host['ip'], self._host['port'])
"#http_" + str(int(netaddr.IPAddress(self._host['ip'])))
