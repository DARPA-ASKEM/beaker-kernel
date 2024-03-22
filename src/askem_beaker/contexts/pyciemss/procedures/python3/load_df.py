import requests

{% for filename, data_url in var_map.items() -%}
with open('{{ filename }}', 'wb') as f:
    f.write(requests.get('{{ data_url }}').content)
{% endfor %}
