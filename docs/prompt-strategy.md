# Prompt Strategy for Review Me

This document outlines the prompt engineering strategy
used to guide AI responses in the Review Me code review assistant. 
The strategy employs a combination of system prompts, user prompts,
and custom tools to generate comprehensive and actionable code reviews.

By following this prompt strategy, Review Me aims to provide consistent, 
high-quality code reviews that enhance the overall development process.

## Overview

The prompt strategy is designed to break down the code review process into three main steps:
1. Initial assessment
2. Detailed file review
3. Final feedback and evaluation

Each step uses carefully crafted prompts and tools to ensure the AI provides relevant and valuable feedback.

## Prompt Types

### System Prompts

System prompts set the context and behavior for the AI in each step of the review process.
They are static and do not change between reviews.

1. **Overview Prompt**: Sets up the AI for the initial assessment of the entire PR.
2. **File Review Prompt**: Prepares the AI for detailed review of individual files.
3. **Final Feedback Prompt**: Guides the AI in synthesizing all feedback and determining the final evaluation.

### User Prompts

User prompts provide specific information about the current PR and guide the AI's response.
All user prompts extend a base template that includes PR context.

1. **Base Template**: 
   - Includes: PR title, description, commit messages, and existing comments
   - Extended by all other user prompts

2. **Overview Template**: 
   - Purpose: Initial assessment of the entire PR
   - Additional variables: None

3. **File Review Template**: 
   - Purpose: Detailed review of a single file
   - Additional variables:
     - Observations from the overview step
     - File context (detailed diff information)

4. **Final Feedback Template**: 
   - Purpose: Synthesize feedback and determine final evaluation
   - Additional variables:
     - Complete list of comments generated from all file reviews

## Custom Tools

Custom tools are used to structure the AI's output at each step of the review process.

1. **Review Files Tool**:
   - Purpose: Make an initial assessment of the entire PR
   - Outputs:
     - Determination of the next review step
     - Categorized observations about the PR (if necessary)
     - List of files requiring further review (if necessary)

2. **Post Feedback Tool**:
   - Purpose: Generate comments for a specific file
   - Outputs:
     - List of comments for the given file diff

3. **Submit Review Tool**:
   - Purpose: Provide final evaluation of the PR
   - Outputs:
     - Overall summary comment
     - Final evaluation (approve, comment, or request changes)

## Prompt Flow

1. **Initial Assessment**:
   - System Prompt: Overview
   - User Prompt: Overview Template
   - Tool: Review Files

2. **File Review** (repeated for each file identified in step 1):
   - System Prompt: File Review
   - User Prompt: File Review Template
   - Tool: Post Feedback

3. **Final Evaluation**:
   - System Prompt: Final Feedback
   - User Prompt: Final Feedback Template
   - Tool: Submit Review

## Best Practices

1. Keep system prompts focused on general behavior and expectations.
2. Use user prompts to provide specific context for each review.
3. Ensure tools output structured data that can be easily processed in subsequent steps.
4. Regularly review and refine prompts based on the quality of AI-generated reviews.
5. Balance between providing enough context for accurate reviews and keeping prompts concise to manage token usage.

## Customization

The prompt strategy can be customized by:
- Adjusting system prompts to focus on specific coding standards or best practices
- Modifying tool schemas to capture additional or different information
- Expanding user prompt templates to include additional PR or repository context

## Maintenance

Regularly update and refine the prompts based on:
- Feedback from development teams
- Changes in coding standards or best practices
- Improvements in AI language model capabilities
