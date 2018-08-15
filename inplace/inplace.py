from __future__ import unicode_literals
import os
from PyInquirer import prompt, Separator, style_from_dict, Token
from subprocess import check_output, call, CalledProcessError
import click
from inplace import __version__

question = {
    "type": "checkbox",
    "message": "Select files to be changed",
    "name": "files",
    "choices": [Separator("==== Matched Files ====")],
}


@click.command()
@click.argument("path", nargs=1)
@click.argument("regex", nargs=1)
@click.version_option(version=__version__)
def entry(path, regex):
    """Find and replace files interactively.

    """
    if not os.path.exists(path):
        click.echo("{} does not exist.".format(path))
        return 1

    click.echo("Compiling the file list... ", nl=False)
    files = check_output(["find", path, "-type", "f", "-print0"])
    click.echo("done.")

    files = files.split(b"\0")[:-1]
    matched_files = []
    max_matches = -1
    click.echo("Finding matches... ", nl=False)
    for f in files:
        f = f.decode()

        arg = 'my $number = $_ =~ {}; print scalar "$number "'.format(regex)
        try:
            o = check_output(["perl", "-ne", arg, f])
        except CalledProcessError as e:
            return e.returncode

        o = b" ".join(o.strip().split())
        if len(o) > 0:
            n = sum(int(i) for i in o)
            matched_files.append((f, n))
            max_matches = max(max_matches, n)

    click.echo("done.")

    if max_matches < 0:
        click.echo("No match has been found.")
        return 0

    num_siz = len(str(max_matches))
    left_siz = num_siz + len(" match(es): ")
    for m in matched_files:
        fmt = "{:" + str(num_siz) + "d}"
        msg = fmt.format(m[1]) + " match(es): {}".format(m[0])
        question["choices"].append({"name": msg})

    answers = prompt(question)
    if "files" not in answers:
        # click.echo("Completed successfully.")
        return 0

    nfails = 0
    for a in answers["files"]:
        filepath = a[left_siz:]
        click.echo(filepath + "... ", nl=False)
        e = call(["perl", "-p", "-i", "-e", regex, filepath])
        if e == 0:
            click.echo("done.")
        else:
            click.echo("FAILED!")
            nfails += 1

    if nfails == 0:
        click.echo("Completed successfully.")
        return 0
    else:
        click.echo("Failed to change {} files!".format(nfails))
        return 1
