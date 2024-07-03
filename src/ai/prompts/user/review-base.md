PR Title: {{context.title}}

PR Body:
{{context.description}}

PR Commits:
{%- for item in context.commit_messages %}
- {{item}}
{%- endfor %}

{% block content %}{% endblock %}