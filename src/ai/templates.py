from jinja2 import Environment, PackageLoader

def load():
    env = Environment(loader=PackageLoader('templates'))
    loaded = dict(
        preamble = env.get_template('preamble.txt')
    )
    return loaded

templates = load()
print(templates['preamble'].render( 
                          title="Test Title",
                          description="Test Description",
                          commit_messages=["Test", "Commit", "Messages"]
                          ))
