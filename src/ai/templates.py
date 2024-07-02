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
                            title = "Test_Title",
                            description = "Test_Description",
                            commit_messages = ["Test", "Commit", "Messages"]
                          )

def overview():
    return preamble() + templates['overview'].render(
                            added_files = "added_files_(test)",
                            deleted_files = "deleted_files_(test)",
                            modified_files = "modified_files_(test)",
                            diffs={
                                "filename1":"diff1",
                                "filename2":"diff2"
                                })

def file_diff():
    with open("src/ai/templates.py", "r") as openfile:
        return preamble() + templates['file_diff'].render(filename="test_file_name",
                                              diff="test_file_diff",
                                              file=openfile.readlines()
                                             )

print(file_diff())
