from jinja2 import Environment, PackageLoader


def preamble(context):
    return Environment(loader=PackageLoader('templates')).get_template('preamble.txt').render(title = context.title,
                                                                                              description = context.description,
                                                                                              commit_messages = context.commit_messages
                                                                                              )

def overview(context):
    return preamble(context) + Environment(loader=PackageLoader('templates')).get_template('overview.txt').render(added_files = context.added_files,
                                                                                                           deleted_files = context.deleted_files,
                                                                                                           modified_files = context.modified_files,
                                                                                                           diffs=context.diffs
                                                                                                           )

def file_diff(context, file_name):
    with open(file_name, "r") as openfile:
        return preamble(context) + Environment(loader=PackageLoader('templates')).get_template('file_diff.txt').render(filename=file_name,
                                                                                                                diff=context.diffs[file_name],
                                                                                                                file=openfile.readlines()
                                                                                                                )
    
def review_summary(context, comments):
    return preamble(context) + Environment(loader=PackageLoader('templates')).get_template('review_summary.txt').render(comment=comments)

