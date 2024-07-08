# Review Me

## Purpose

Review Me is an AI-powered code review assistant deployed as a GitHub action. It aims to streamline the code review
process by providing an initial layer of automated, high-quality feedback on pull requests before human reviewers
intervene. This allows human reviewers to focus on more complex aspects of code changes, ultimately improving code
quality and reducing review time.

## Key Features

- Automated, comprehensive code review for pull requests
- Support for multiple programming languages
- Immediate, actionable feedback to developers
- Prioritization of substantial, valuable feedback
- Customizable review criteria and focus areas [Coming soon!]

## Process

> For a detailed explanation of how Review Me uses prompts and tools to generate reviews,
> please see our [Prompt Strategy Document](./docs/prompt-strategy.md).

The system employs a three-step approach leveraging the Anthropic API:

### Step 1: Initial Filtering

- Performs an initial assessment of the entire PR diff
- Identifies files requiring more careful review based on predefined criteria
- Utilizes a custom `review_files` tool to submit files for detailed review

### Step 2: Detailed File Review

- Conducts in-depth reviews of individual files identified in Step 1
- Provides specific, actionable comments on code changes
- Employs a custom `post_feedback` tool to aggregate comments for final evaluation

### Step 3: Overall Summary and Evaluation

- Synthesizes individual comments into a comprehensive review summary
- Determines the final review action (approve, comment, or request changes)
- Uses a custom `submit_review` tool to submit the final evaluation

## Usage

To use Review Me in your GitHub repository, follow these steps:

1. Add the Review Me action to your repository's workflow file (e.g., `.github/workflows/review-me.yml`).
2. Set up the necessary secrets and variables in your repository settings.
3. Trigger the review by commenting `/review-me` on a pull request.

### Prerequisites

- An Anthropic API key (Claude model access required)

### Setup

1. Add an `ANTHROPIC_API_KEY` to your repository secrets.
2. (Optional) Specify a persona as a repository variable named `PERSONA`.

### Example Action Definition

Create or update the file `.github/workflows/review-me.yml` in your repository with the following content:

```yaml
name: LLM Code Review

on:
  issue_comment:
    types: [ created ]

permissions:
  contents: read
  pull-requests: write
  issues: write

jobs:
  review:
    if: github.event.issue.pull_request && github.event.comment.body == '/review-me'
    runs-on: ubuntu-latest
    env:
      PERSONA: ${{ vars.PERSONA }}
    steps:
      - uses: actions/checkout@v4
        with:
          ref: refs/pull/${{ github.event.issue.number }}/merge
          fetch-depth: 0

      - name: LLM Code Review
        uses: FyZyX/review-me@v1
        with:
          github_token: ${{ github.token }}
          anthropic_api_key: ${{ secrets.ANTHROPIC_API_KEY }}
```

### Triggering a Review

To trigger a review on a pull request:

1. Open the pull request you want to review.
2. Add a comment with the text `/review-me`.
3. The action will run automatically, and the AI will submit its review to pull request once complete.

## Configuration

Review Me offers several configuration options to customize its behavior.
These can be set as inputs in your workflow file or as repository variables/secrets.

### Repository Variables

- `PERSONA`: Set this to choose a specific reviewer persona.
  Available options can be found in the [`persona` prompts](./src/ai/prompts/persona).

### Repository Secrets

- `ANTHROPIC_API_KEY`: Your Anthropic API key for accessing the Claude model.

## Key Goals

1. Enhance code quality through consistent, thorough reviews
2. Reduce time spent on trivial fixes during human reviews
3. Provide immediate, actionable feedback to developers
4. Support multiple programming languages and coding styles
5. Prioritize valuable, substantive feedback over minor issues

## Current Challenges and Ongoing Improvements

- Ensuring consistently helpful and relevant feedback
- Avoiding redundant comments on issues already addressed in the code
- Balancing thorough feedback with conciseness
- Determining optimal context needed at each step for holistic review

## Future Work

### Near-term

- Allow users to define custom review rules and priorities
- Implement a feedback loop to improve review quality based on user interactions
- Enhance the AI's ability to understand relationships between different files in a PR
- Provide insights on architectural impacts of changes

### Long-term

- Offer AI-generated code suggestions to address identified issues
- Develop capabilities to suggest refactoring strategies for complex code
- Implement automated documentation updates based on code modifications
- Explore capabilities for generating unit tests based on code changes
- Develop a dashboard for tracking review statistics and trends
- Implement a chat-like interface for developers to ask questions about the review

## Contributing

We currently have no structured contribution process,
but we are always open to suggestions in the form of issues or pull requests.

## License

Not currently licensed.
