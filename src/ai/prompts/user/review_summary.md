{% extends 'user/review-base.md' %}

{% block content -%}
Current Feedback:
{% for comment in comments -%}
{{comment}}
{% endfor -%}
{% endblock %}