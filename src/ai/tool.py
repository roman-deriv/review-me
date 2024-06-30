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
