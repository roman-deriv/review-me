{% extends 'review-base.md' %}

{% block content -%}
Original file: {{ review_request.path }}
Summary of changes in this file: {{ review_request.changes }}
Changes in related files: {{ review_request.related_changed }}

Hunks:
{% for hunk in review_request.hunks -%}
Hunk {{ loop.index }}:
    Start Line: {{ hunk.start_line }}
    End Line: {{ hunk.end_line }}
    Changed Lines {{ hunk.changed_lines }}
----------
{%- endfor %}

Diff for file: {{ review_request.path }}
{{ review_request.diff }}
{% endblock %}