# from __future__ import unicode_literals
import sys
from PyInquirer import prompt, Separator
from subprocess import check_output, call
from tqdm import tqdm
import click

question = {
    "type": "checkbox",
    "message": "Select files to be changed",
    "name": "files",
    "choices": [Separator("==== Matched Files ====")],
}


@click.command()
@click.argument("dir", nargs=1)
@click.argument("regex", nargs=1)
@click.version_option(version="0.0.1")
def entry(dir, regex):
    files = check_output(["find", dir, "-type", "f", "-print0"])

    files = files.split(b"\0")[:-1]
    matched_files = []
    max_matches = -1
    for f in tqdm(files, desc="Searching"):
        f = f.decode()

        arg = 'my $number = $_ =~ {}; print scalar "$number "'.format(regex)
        o = check_output(["perl", "-ne", arg, f])
        o = b" ".join(o.strip().split())
        if len(o) > 0:
            n = sum(int(i) for i in o)
            matched_files.append((f, n))
            max_matches = max(max_matches, n)

    if max_matches < 0:
        return

    num_siz = len(str(max_matches))
    left_siz = num_siz + len(" match(es): ")
    for m in matched_files:
        fmt = "{:" + str(num_siz) + "d}"
        msg = fmt.format(m[1]) + " match(es): {}".format(m[0])
        question["choices"].append({"name": msg})

    answers = prompt(question)
    if "files" not in answers:
        return 0

    nfails = 0
    for a in answers["files"]:
        filepath = a[left_siz:]
        sys.stdout.write(filepath + "... ")
        e = call(["perl", "-p", "-i", "-e", regex, filepath])
        if e == 0:
            print("done.")
        else:
            print("FAILED!")
            nfails += 1

    if nfails == 0:
        print("Completed successfully.")
        return 0
    else:
        print("Failed to change {} files!".format(nfails))
        return 1
