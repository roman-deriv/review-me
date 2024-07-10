# Development Challenges and Solutions

## 1. Comment Placement in Git Diffs

### Problem
The LLM frequently generated comments with line numbers that didn't align with the actual git diff, causing errors when trying to post reviews.

### Solution
Developed a custom algorithm to adjust comment placements:
1. Parse git diff hunks to understand the structure of changes.
2. For each comment:
   - Identify the nearest relevant hunk.
   - Adjust the comment's line numbers to fit within the hunk's boundaries.
   - If no suitable hunk is found, discard the comment.

This approach significantly reduced errors and ensured comments were always placed on changed lines.

## 2. Balancing Comment Quality and Quantity

### Problem
Initial reviews were often filled with superficial praise or minor suggestions, diluting the value of the feedback.

### Solution
Implemented a categorization system for comments:
1. Defined a set of categories (e.g., CRITICAL, PERFORMANCE, MAINTAINABILITY).
2. Modified prompts to require the LLM to categorize each comment.
3. Developed a filtering system to prioritize comments based on their categories.

This allowed us to focus on substantial feedback and reduce noise in the reviews.

## 3. Maintaining Cross-File Context

### Problem
The LLM struggled to understand the implications of changes across multiple files, leading to uncertain or incomplete feedback.

### Current Approach
We're experimenting with several strategies:
1. Grouping related code chunks from different files for review.
2. Developing a system to summarize key changes and their potential impacts across the codebase.
3. Investigating ways to provide more comprehensive context without exceeding token limits.

This remains an ongoing challenge, and we're continually refining our approach.

## 4. Prompt Engineering for Consistent, High-Quality Reviews

### Problem
Crafting effective prompts that consistently produce valuable reviews proved challenging.

### Solution
Adopted an iterative approach to prompt engineering:
1. Continuously refined prompts based on review outcomes.
2. Implemented a flexible prompt template system to allow easy adjustments and experimentation.

This process has led to steady improvements in review quality and consistency.
