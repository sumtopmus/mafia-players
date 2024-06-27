from dynaconf import Dynaconf

settings = Dynaconf(
    settings_files=['settings.toml'],
    secrets=['.secrets.toml'],
    environments=True
)
