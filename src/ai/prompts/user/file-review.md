{% extends 'review-base.md' %}

{% block content -%}
Original file: {{ file_context.path }}
Summary of changes in this file: {{ file_context.changes }}
Changes in related files: {{ file_context.related_changed }}

Hunks:
{% for hunk in file_context.patch.hunks -%}
Hunk {{ loop.index }}:
    Start Line: {{ hunk.start_line }}
    End Line: {{ hunk.end_line }}
    Changed Lines {{ hunk.changed_lines }}
----------
{%- endfor %}

> **NOTE**: We are already aware of the following observations.
> Do not make any comments related to the issues.
> Keep your comments focused on specific, actionable items related to the implementation details.
{% for observation in observations -%}
- [{{ observation.tag }}] {{ observation.comment }}:
{%- endfor %}

Diff for file: {{ file_context.path }}
{{ file_context.patch.diff }}
{% endblock %}
