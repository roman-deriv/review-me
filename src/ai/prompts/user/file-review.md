{% extends 'review-base.md' %}

{% block content -%}
Original file: {{ review_request.path }}
{% for line in source_code -%}
{{ loop.index }} | {{ line }}
{%- endfor %}
----------

Changes in related files: {{ review_request.related_changed }}
Summary of changes in this file: {{ review_request.changes }}
Diff for file: {{ review_request.path }}
{{ review_request.diff }}
{% endblock %}