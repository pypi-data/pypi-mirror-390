import cloup

from .. import jinja, questions, template, trees
from .cli import cli


#
# mk-scaffold clone [OPTIONS] TEMPLATE
#
@cli.command(help="Clone and templatize a repository.")
@cloup.option(
    "-i",
    "--input-file",
    "answer_file",
    metavar="FILE",
    type=cloup.Path(exists=True, dir_okay=False, readable=True),
    help="Location of a yaml input file, usually named '.answers.yml', with answers to the questions.",
)
@cloup.option(
    "-o",
    "--output-dir",
    metavar="DIR",
    default=".",
    type=cloup.Path(file_okay=False, dir_okay=True),
    show_default=False,
    help="Where to output the generated files. [default: current directory]",
)
@cloup.option(
    "--filename",
    "template_filename",
    metavar="FILENAME",
    default="scaffold.yml",
    show_default=True,
    help="Filename of the scaffold file to use.",
)
@cloup.option(
    "-b",
    "--branch",
    metavar="BRANCH",
    default=None,
    show_default=False,
    help="Checkout git BRANCH of git repository",
)
@cloup.argument(
    "template_path",
    nargs=1,
    metavar="TEMPLATE",
    type=cloup.Path(),
    help="Directory or git repository that contains 'scaffold.yml' template file",
)
def clone(**kwargs):
    tpl = template.Template(**kwargs)

    # Get the main template (eg: scaffold.yml) data from possible
    # locations (folder, git, ...).
    tpl.find()
    tpl.read()
    tpl.validate()
    tpl.recurse()

    env, ctx = jinja.get(tpl)

    # Load the answers in the same file as the questions since
    # the "scaffold.yml" can already have an answers section from
    # the scaffold.yml file
    tpl.load_answers(kwargs["answer_file"])

    ctx = questions.prompt(env, ctx, tpl)

    trees.clone(env, ctx, tpl, kwargs["output_dir"])
    trees.process(env, ctx, tpl, kwargs["output_dir"])
