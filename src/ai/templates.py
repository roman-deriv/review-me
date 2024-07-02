from jinja2 import Environment, PackageLoader

def load_templates():
    env = Environment(loader=PackageLoader('templates'))
    loaded = []
    loaded.append(env.get_template('test.txt'))
    loaded.append(env.get_template('test2.txt'))
    return loaded

templates = load_templates()
print(templates[0].render(testvar="test#1"))
print(templates[1].render(testvar="test#2"))
