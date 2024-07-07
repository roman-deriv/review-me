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

## Usage

[Provide usage instructions, including how to set up the GitHub action]

## Configuration

[Explain how to configure the tool, including any customizable options]

## Contributing

We currently have no structured contribution process,
but we are always open to suggestions in the form of issues or pull requests.

## License

Not currently licensed.
