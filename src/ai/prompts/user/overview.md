{% extends 'review-base.md' %}

{% block content -%}
{%- if context.added_files -%}
Files Added:
{%- for file in context.added_files %}
- {{ file }}
{%- endfor %}
{%- endif -%}

{%- if context.deleted_files -%}
Files Deleted:
{%- for file in context.deleted_files %}
- {{ file }}
{%- endfor %}
{%- endif -%} 

{% if context.modified_files %}
Files Modified:
{%- for file in context.modified_files %}
- {{ file }}
{%- endfor %}
{% endif %} 

Changes:
{%- for filename, diff in context.diffs.items() -%}
Diff for file: {{filename}}
{{diff}}
{%- endfor %}
{%- endblock %}