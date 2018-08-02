gopher://{{data['ip']}}/
Dirs:
{% for dir in [f for f in self._host['data']['files'] if f['type'] == '1'] -%}
 + {{dir['path']}}
{% endfor -%}
Other nodes:
{% for file in [f for f in self._host['data']['files'] if f['type'] != '1' and f['type'] != 'i'] -%}
 + {{file['path']}}
     {{file['name']}}
{% endfor -%}
Geo: {{data['geo']['country']}}/{{data['geo']['city']}}