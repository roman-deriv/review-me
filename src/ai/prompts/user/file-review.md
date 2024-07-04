{% extends 'review-base.md' %}

{% block content -%}
Original file: {{ file.path }}
{% for line in source_code -%}
{{ loop.index }} | {{ line }}
{%- endfor %}
----------

Changes in related files: {{ file.related_changed }}
Summary of changes in this file: {{ file.changes }}
Diff for file: {{ file.path }}
{{ context.diffs[file.path] }}
{% endblock %}