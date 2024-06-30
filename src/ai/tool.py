review_files = {
    "name": "review_files",
    "description": "Review a list of files more carefully. "
                   "It should be used whenever the user needs a PR review.",
    "input_schema": {
        "type": "object",
        "properties": {
            "files": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "filename": {
                            "type": "string",
                            "description": "Name of the file to review"
                        },
                        "reason": {
                            "type": "string",
                            "description": "The reason or rationale for the review"
                        }
                    },
                    "required": ["filename", "reason"]
                }
            }
        },
        "required": ["files"]
    }
}
post_feedback = {
    "name": "post_feedback",
    "description": "Create GitHub pull request review comments from the provided "
                   "feedback. This tool should be used to post detailed, "
                   "line-specific comments on code changes. Each feedback item "
                   "should correspond to a specific location in the code, identified "
                   "by line number. Use this for constructive feedback, suggestions "
                   "for improvement, or highlighting potential issues in the code. "
                   "Ensure comments are clear, specific, and actionable.",
    "input_schema": {
        "type": "object",
        "properties": {
            "feedback": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "line": {
                            "type": "integer",
                            "description": "The line number in the file to comment on. "
                                           "This can be omitted for file comments."
                        },
                        "side": {
                            "type": "string",
                            "enum": ["LEFT", "RIGHT"],
                            "description": "LEFT for original code, "
                                           "RIGHT for modified code"
                        },
                        "start_line": {
                            "type": "integer",
                            "description": "Start line for multi-line comments"
                        },
                        "start_side": {
                            "type": "string",
                            "enum": ["LEFT", "RIGHT"],
                            "description": "Side for the start line in multi-line "
                                           "comments"
                        },
                        "body": {
                            "type": "string",
                            "description": "The actual feedback or comment on this "
                                           "section of code"
                        },
                    },
                    "required": ["body"]
                }
            }
        },
        "required": ["feedback"]
    }
}