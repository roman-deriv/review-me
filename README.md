# Review Me

## Purpose
The project aims to streamline the code review process by providing an initial layer of automated,
high-quality feedback, allowing human reviewers to focus on more complex aspects of the code changes.

An automatic code reviewer AI assistant that is deployed as a GitHub action.
The goal is to provide comprehensive, actionable feedback on pull requests before human reviewers look at the code.

## Process

The system uses a three-step approach leveraging the Anthropic API:

### Step 1 (Initial Filtering):

- Performs an initial assessment of the entire PR diff.
- Identifies which files need more careful review based on certain criteria.
- Uses a custom tool (`review_files`) to submit files for detailed review.

### Step 2 (Detailed File Review):

- Reviews individual files identified in step 1.
- Provides specific, actionable comments on code changes.
- Uses a custom tool (`post_feedback`) to aggregate the comments in preparation for final evaluation.

### Step 3 (Overall Summary and Evaluation):

- Synthesizes individual comments into a comprehensive review summary.
- Determines the final review action (approve, comment, or request changes).
- Uses a custom tool (`submit_review`) to submit the final evaluation.

## Key Goals:
- Reduce time wasted on trivial fixes during human reviews.
- Handle multiple programming languages.
- Provide immediate, actionable feedback to developers.
- Prioritize valuable, substantive feedback.

## Current Challenges:
- Ensuring feedback is consistently helpful and relevant.
- Avoiding comments on issues that are already addressed in the code.
- Balancing between providing thorough feedback and being concise.
- Determining the right context needed at each step to ensure a holistic review.
