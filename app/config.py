import toml

config = toml.load("config.toml")

def save():
    toml.dump(config, open("config.toml", "w"))