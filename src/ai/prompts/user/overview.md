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
{%- for filename, patch in context.patches.items() -%}
Diff for file: {{filename}}
{{ patch.diff }}
{%- endfor %}
{%- endblock %}