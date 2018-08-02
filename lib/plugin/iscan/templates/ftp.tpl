ftp://{{data['username']}}:{{data['password']}}@{{data['ip']}}
{% for filename in data['files'] -%}
 + {{ filename }}
{% endfor -%}
Geo: {{data['geo']['country']}}/{{data['geo']['city']}}

