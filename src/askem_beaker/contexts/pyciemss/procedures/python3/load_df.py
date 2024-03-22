import requests

{% for filename, data_url in name_to_url.items() -%}
with open('{{ filename }}', 'wb') as f:
    f.write(requests.get('{{ data_url }}').content)
{% endfor %}
