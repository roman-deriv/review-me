from jinja2 import Environment, PackageLoader

def load_templates():
    env = Environment(loader=PackageLoader('templates'))
    loaded = []
    loaded.append(env.get_template('Preamble.txt'))
    loaded.append(env.get_template('test2.txt'))
    return loaded

templates = load_templates()
print(templates[0].render( 
                          title="Test Title",
                          description="Test Description",
                          commit_messages=["Test", "Commit", "Messages"]
                          ))
