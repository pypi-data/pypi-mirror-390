
import inspect
from datetime import datetime

import netdot
from netdot import (
    CSVReport,
    NetdotAPIDataclass,
    Repository,
    UnitOfWork,
    config,
    exceptions,
)


def generate_markdown_docs_ENV_VARs():
    """Generate documentation for all of the default values in netdot.config.

    > This is useful for understanding what flags are available, and what their default values are.
    """
    return f"""

# Netdot Python API Environment Variables
<a id="netdot-python-api-environment-variables"></a>

> Generated using `netdot.config.help()`
>
{_version_and_date_as_markdown_note()}

```
{config.help_str()}
```
"""

def generate_markdown_docs(heading=True):
    # TODO Consider refactoring so that there is a method that returns a nested dictionary with all all public methods and public fields. That way, we can easily run a change-detection test -- this is effectively our public API, so it would be nice to have visibility over when it changes (e.g. fail CI/CD unless a certain 'updated_public_api=True' build parameter is provided).
    lines = list()
    if heading:
        lines.append('# Netdot Python API Generated Documentation\n')
        lines.append('<a id="netdot-python-api-generated-documentation"></a>')
        lines.append(_version_and_date_as_markdown_note())
        lines.append('>')
        lines.append('> Netdot Python API contains many generated methods.')
        lines.append(
            '> This documentation is intended to help you understand what is available.'
        )
        lines.append('\n\n')
    Repository._prepare_class()  # Ensure that the Repository class is prepared for use
    lines.append(_generate_markdown_for_class(Repository))
    lines.append(_generate_markdown_for_class(UnitOfWork))
    lines.append(_generate_markdown_for_class(CSVReport))

    for dataclass in sorted(NetdotAPIDataclass.__subclasses__(), key=lambda x: x.__name__):
        lines.append(_generate_markdown_for_class(dataclass))
    return (
        '\n\n' + '\n'.join(filter(None, lines)) + '\n\n'
    )  # Why '\n\n' newline padding? In case this markdown is concatenated with other markdown files.


def _version_and_date_as_markdown_note():
    return f'> Version {netdot.__version__} documentation generated on {datetime.now().strftime("%b %d, %Y at %I:%M%p %Z")}'


def _generate_markdown_for_class(
    cls,
    internal_methods_can_skip=[  # These 'internal' methods are not very useful to publicly document
        'to_DTO',
        'from_DTO',
        'with_repository',
        'table_header',
        'as_table_row',
    ],
):
    lines = list()
    lines.append(f'## class `netdot.{cls.__name__}`\n')
    lines.append(f'<a id="class-netdot{cls.__name__.lower()}"></a>\n')
    if hasattr(cls, '_updatable_fields'):
        lines.append('### Attributes\n')
        fields = [
            field if field.name in cls._updatable_fields() else None
            for field in cls.__dataclass_fields__.values()
        ]
        fields = list(filter(None, fields))
        if fields:
            lines.append('| Attribute | Type | Default |')
            lines.append('| --------- | ---- | ------- |')
            for field in filter(None, fields):
                if field.default is not None:
                    lines.append(
                        f'| {field.name} | {field.type.__name__} | {field.default} |'
                    )
                else:
                    lines.append(f'| {field.name} | {field.type.__name__} |  |')
        else:
            lines.append('*No public attributes.*')
        lines.append('\n')
    methods = inspect.getmembers(cls, predicate=inspect.isfunction)
    methods = list(
        filter(
            lambda method_tuple:
            # Do provide documentation for Repository constructor
            method_tuple[0] == '__init__'
            and cls == Repository
            or (
                # Filter 'private' (start with _)
                not method_tuple[0].startswith('_')
                # Filter ALL_CAPS_FIELDS (these are constants)
                and not method_tuple[0].upper() == method_tuple[0]
                # Filter 'internal methods that can be skipped'
                and method_tuple[0] not in internal_methods_can_skip
            ),
            methods,
        )
    )
    _assert_methods_have_docstrings(methods, cls.__name__)
    if methods:
        lines.append('### Methods\n')
    for name, method in methods:
        lines.append(f'#### {cls.__name__}.{name}\n')
        lines.append(f'> ```{name}{inspect.signature(method)}```')
        lines.append('\n```')
        lines.append(inspect.getdoc(method).strip())
        lines.append('```\n')
    return '\n'.join(filter(None, lines))


def _assert_methods_have_docstrings(methods, class_name):
    result = list(filter(lambda tup: tup[1].__doc__ is None, methods))
    if result:
        raise exceptions.NetdotError(
            f'{class_name} is missing docstrings for methods: {[method[0] for method in result]}'
        )
