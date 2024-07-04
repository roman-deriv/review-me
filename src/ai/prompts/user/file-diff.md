{% extends 'review-base.md' %}

{% block content -%}
Additional Context: {{ file.additional_context }}
Original file: {{ file.path }}
{% for line in source_code -%}
{{ loop.index }} | {{ line }}
{%- endfor %}
----------

Summary of Changes: {{ file.changes }}
Diff for file: {{ file.path }}
{{ context.diffs[file.path] }}
{% endblock %}