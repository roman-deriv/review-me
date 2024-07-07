# Prompt Strategy

Uses prompt engineering to guide the AI's responses.

## Prompt Templates

Utilizes templates for structuring prompts and organizing review data.

## System Prompts

- Overview (initial assessment)
- File review
- Final feedback

## User Prompts

All user templates require the PR context for rendering the base template.

- Base: All other templates extend this
- Overview
    - Requires no additional template variables
- File review: Run once per file from the list of files generated in the overview step
    - Observations: Generated from the overview step
    - File context: More detailed information about each fill diff
- Final feedback
    - Comments: The complete list of comment generated from all files in the file review step

## Tool Use

- Review files
    - Make an initial assessment of the PR as a whole
    - Provide categorized observations (if necessary)
    - List the files that require further review (if necessary)
- Post feedback
    - Generate a list of comments for the given file diff
- Submit review
    - Summarize the feedback from previous steps into an overall comment
    - Determine a final evaluation of pull request
