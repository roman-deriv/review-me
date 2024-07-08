{% extends 'review-base.md' %}

{% block content -%}
## Prioritized Feedback

These comments will be posted as individual review comments, 
they are just here for reference and context.

{% for comment in prioritized_comments -%}
- {{ comment }}
{% endfor -%}

## Remaining Feedback to Summarize

These are additional comments that were generated, but will not be posted individually.
Summarize this feedback primarily so that the author of the PR is at least broadly aware of this feedback as well.

{% for comment in comments -%}
- {{ comment }}
{% endfor -%}
{% endblock %}