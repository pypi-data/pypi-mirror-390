
from assertpy import assert_that

import netdot
from netdot import gen_docs


def test_generate_repository_api_docs():
    netdot.initialize()
    
    docs = gen_docs._generate_markdown_for_class(netdot.Repository)
    
    assert_that(docs).contains('create_host')

def test_generate_markdown_API_docs(generate_docs):
    # Arrange
    netdot.initialize()

    # Act
    docs = gen_docs.generate_markdown_docs()

    # ! SIDE EFFECT - Write updated documentation to file
    if generate_docs:
        with open('docs/generated-api-docs.md', 'w') as f:
            f.write(docs)

    # Assert
    assert_that(docs[:1000].lower()).contains('# netdot python api generated documentation')
    assert_that(docs).contains('add_device')


def test_generate_ENV_VARs_help_docs(generate_docs):
    # Act
    docs = gen_docs.generate_markdown_docs_ENV_VARs()

    # ! SIDE EFFECT - Write updated documentation to file
    if generate_docs:
        with open('docs/generated-env-var-docs.md', 'w') as f:
            f.write(docs)

    # Assert
    assert_that(docs).contains('NETDOT_CLI_TERSE')
    assert_that(docs).contains('SERVER_URL')


def test_generate_dist_readme(generate_docs):
    # Arrange
    netdot.initialize()
    REPLACEMENTS = {
        './user-guide.md': '#user-guide',
        './changelog.md': '#changelog',
        './generated-api-docs.md': '#netdot-python-api-generated-documentation',
        './generated-env-var-docs.md': '#netdot-python-api-environment-variables',
    }

    # ! SIDE EFFECT - Write updated documentation to file
    if generate_docs:
        with open('dist-README.md', 'w') as f:
            with open('docs/user-guide.md', 'r') as user_guide_f:
                text = user_guide_f.read()
                for old, new in REPLACEMENTS.items():
                    text = text.replace(old, new)
                f.write(text)
                f.write('\n\n')
            with open('docs/changelog.md', 'r') as changelog_f:
                text = changelog_f.read()
                text = text.replace('./user-guide.md#proposed-changes-pickle-file','#proposed-changes-pickle-file')
                text = text.replace('./user-guide.md#example-8-plan-and-create-a-new-netdot-site','#example-8-plan-and-create-a-new-netdot-site')
                for old, new in REPLACEMENTS.items():
                    text = text.replace(old, new)
                f.write(text)
                f.write('\n\n')
            f.write(gen_docs.generate_markdown_docs())
            f.write('\n\n')
            f.write(gen_docs.generate_markdown_docs_ENV_VARs())
            f.write('\n\n')
