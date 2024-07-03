{% extends 'user/review-base.md' %}

{% block content -%}
Original file: {{filename}}
{% for line in file -%}
{{loop.index}} | {{line}}
{%- endfor %}
----------

Diff for file: {{filename}}
{{diff}}
{% endblock %}