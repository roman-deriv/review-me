from jinja2 import Environment, PackageLoader

def load():
    env = Environment(loader=PackageLoader('templates'))
    loaded = dict(
        preamble = env.get_template('preamble.txt'),
        overview = env.get_template('overview.txt'),
        file_diff = env.get_template('file_diff.txt')
    )
    return loaded

templates = load()

def preamble():
    return templates['preamble'].render( 
                            title = "Test Title",
                            description = "Test Description",
                            commit_messages = ["Test", "Commit", "Messages"]
                          )

def overview():
    return preamble() + templates['overview'].render(
                            added_files = "added files (test)",
                            deleted_files = "deleted files (test)",
                            modified_files = "modified files (test)",
                            diffs={
                                "filename1":"diff1",
                                "filename2":"diff2"
                                })

def file_diff():
    with open("src/ai/templates.py", "r") as openfile:
        return templates['file_diff'].render(file=openfile.readlines(),
                                             )

print(file_diff())
