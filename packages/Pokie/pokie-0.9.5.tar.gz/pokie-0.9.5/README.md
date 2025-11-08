# Welcome to Pokie


[![Tests](https://github.com/oddbit-project/pokie/workflows/Tests/badge.svg)](https://github.com/oddbit-project/pokie/actions)
[![pypi](https://img.shields.io/pypi/v/pokie.svg)](https://pypi.org/project/pokie/)
[![license](https://img.shields.io/pypi/l/pokie.svg)](https://git.oddbit.org/OddBit/pokie/src/branch/master/LICENSE)


Pokie is an API-oriented modular web framework built on top of [Flask](https://github.com/pallets/flask/),
[Rick](https://git.oddbit.org/OddBit/rick) and [Rick-db](https://git.oddbit.org/OddBit/rick_db) libraries, following three-layer and clean architecture
design principles.

It features a object-oriented design, borrowing from common patterns found in other languages, such as
dependency injection, service location, factories and object composition. It also offers the following functionality:

- Modular design;
- Dependency registry; 
- CLI command support;
- Jobs (objects invoked periodically to perform a task);
- Fixtures;
- Unit testing support with pytest;
- Code generation;
- REST-oriented service design; 
- Compatibility with Flask;



For detailed information, please check the [Documentation](https://oddbit-project.github.io/pokie/)

# TL; DR; tutorial

1. Create the application entrypoint, called *main.py*:

```python
from rick.resource.config import EnvironmentConfig
from pokie.config import PokieConfig
from pokie.core import FlaskApplication
from pokie.core.factories.pgsql import PgSqlFactory


class Config(EnvironmentConfig, PokieConfig):
    # @todo: add your config options or overrides here
    pass


def build_pokie():
    # load configuration from ENV
    cfg = Config().build()

    # modules to load & initialize
    modules = [
        # @ todo: add your modules here

    ]

    # factories to run
    factories = [
        PgSqlFactory,
        # @todo: add additional factories here
    ]

    # build app
    pokie_app = FlaskApplication(cfg)
    flask_app = pokie_app.build(modules, factories)
    return pokie_app, flask_app


main, app = build_pokie()

if __name__ == '__main__':
    main.cli()
```

2. Use our application to scaffold a module:

```shell
$ python3 main.py codegen:module my_module_name .
```

3. Add your newly created module to the module list on *main.py*:

```python
    (...)
    # modules to load & initialize
    modules = [
        'my_module_name',  # our newly created module
        
    ]
    (...)
```

4. Implement the desired logic in the module



# Running tests with tox

1. Install tox & tox-docker:
```shell
$ pip install -r requirements-test.txt
```

2. Run tests:
```shell
$ tox [-e py<XX>]
```
 