# Review Me

## Purpose

Review Me is an AI-powered code review assistant deployed as a GitHub action. It aims to streamline the development process by providing rapid, actionable feedback on code changes before human review. This tool is designed to catch minor issues and obvious improvements early, allowing developers to iterate quickly and human reviewers to focus on more complex aspects of code changes.

## Philosophy

Review Me is not meant to replace human code reviews. Instead, it serves as a complementary tool in the development process, acting more like a pair-programming assistant than a traditional code review bot. Our goal is to enhance the entire review process, not to automate it entirely.

## Key Features

- Instant, comprehensive code review for pull requests
- Support for multiple programming languages
- Specific, multi-line comments packaged into a complete review
- Prioritization of substantial, valuable feedback
- Iterative review support: push code, get feedback, improve, repeat
- Easy integration with existing GitHub workflows

## Process

The system employs a three-step approach leveraging the Anthropic API:

1. **Initial Filtering**: Assesses the entire PR diff and identifies files needing detailed review.
2. **Detailed File Review**: Conducts in-depth reviews of identified files, providing specific comments.
3. **Overall Summary and Evaluation**: Synthesizes comments into a comprehensive review summary.

For a detailed explanation of our prompt strategy, see our [Prompt Strategy Document](./docs/prompt-strategy.md).

## What Sets Review Me Apart

- Focus on augmenting, not replacing, human reviews
- Support for iterative development and rapid feedback cycles
- Comprehensive review with specific, multi-line comments
- Philosophy of improving the entire review process, not just automating parts of it

## Usage

To use Review Me in your GitHub repository, follow these steps:

1. Add the Review Me action to your repository's workflow file (e.g., `.github/workflows/review-me.yml`).
2. Set up the necessary secrets and variables in your repository settings.
3. Trigger the review by commenting `/review-me` on a pull request.

### Prerequisites

- An [Anthropic](https://www.anthropic.com/) API key (Claude model access required)
- A [Voyage AI](https://www.voyageai.com) API Key

### Setup

1. Add an `ANTHROPIC_API_KEY` to your repository secrets.
1. Add a `VOYAGE_API_KEY` to your repository secrets.
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
          voyage_api_key: ${{ secrets.VOYAGE_API_KEY }}
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
- `VOYAGE_API_KEY`: Your Anthropic API key for accessing the Claude model.

## Key Goals

1. Accelerate development cycles through instant, actionable feedback
2. Enhance code quality by catching minor issues early
3. Streamline human reviews by addressing trivial fixes beforehand
4. Support iterative development with rapid feedback loops
5. Maintain the value of human insight in the review process

## Current Challenges and Ongoing Improvements

- Ensuring consistently helpful and relevant feedback
- Avoiding redundant comments on issues already addressed in the code
- Balancing thorough feedback with conciseness
- Determining optimal context needed at each step for holistic review

## Future Work

### Near-term

- Allow users to define custom review rules and priorities
- Use semantic similarity to group related hunks of code for review, instead of going file by file
- Enhance the AI's ability to understand relationships between different files in a PR
- Gather user feedback by capturing replies to review comments and allowing the LLM to respond as needed
- Provide insights on architectural impacts of changes

### Long-term

- Offer AI-generated code suggestions to address identified issues
- Develop capabilities to suggest refactoring strategies for complex code
- Implement automated documentation updates based on code modifications
- Explore capabilities for generating unit tests based on code changes
- Develop a dashboard for tracking review statistics and trends
- Implement a chat-like interface for developers to ask questions about the review

## Contributing

We welcome contributions and ideas that align with our vision of enhancing the code review process while maintaining the crucial role of human reviewers. Please feel free to open issues or submit pull requests.

## License

Not currently licensed.
