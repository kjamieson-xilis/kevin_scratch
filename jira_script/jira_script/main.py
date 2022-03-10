import pprint

from blessed import Terminal
import click
import jira
from rich.console import Console
from rich.table import Table

import webbrowser
PP = pprint.PrettyPrinter(indent=2)
"""
The JIRA api reads from credentials in  ~/.netrc by default
Create an API token and place it in .netrc, example:

machine xilis.atlassian.net
login kevin.jamieson@xilis.net
password <API TOKEN STRING>
"""
OPTIONS = {'server': 'https://xilis.atlassian.net'}
SES_BOARD = 8


def get_active_sprint(board_id):
    gh = jira.client.GreenHopper(OPTIONS)
    sprints = gh.sprints(board_id)
    print(sprints)
    active_sprint = [x for x in sprints if x.state == 'ACTIVE']
    if active_sprint:
        return active_sprint[0]
    else:
        return None


def get_tickets():
    j = jira.JIRA(OPTIONS)
    JQL = f'statusCategory != "Done" AND assignee in (currentUser()) order by priority'
    results = j.search_issues(JQL, expand="Names")
    infra_tickets = []
    for entry in results:
            infra_tickets.append(entry)
    return infra_tickets

def show_tickets():
    infra = get_tickets()
    console = Console()
    atp_table = Table(show_header=True, header_style="bold magenta")
    atp_table.add_column("Key")
    atp_table.add_column("Summary")
    atp_table.add_column("Status")
    atp_table.add_column("Priority")
    atp_table.add_column("Sprint")

    infra_table = Table(show_header=True, header_style="bold green")
    infra_table.add_column("Key")
    infra_table.add_column("Summary")
    infra_table.add_column("Status")
    infra_table.add_column("Priority")
    for x in infra:
        infra_table.add_row(x.key, x.fields.summary, x.fields.status.name, x.fields.priority.name)

    console.print(infra_table)

def render(term, data, idx):
    leftpad = 10
    result = term.home + term.normal + term.clear_eos
    result += term.move_right(leftpad)
    for x in data:
        result += x
        result += term.move_down(1)
        result += term.move_left(len(x))
    result += term.home + term.move_xy(2, idx)
    result += '>'
    return result

def main():
    #show_tickets()
    stuff = ["something", "else", "entirely"]
    term = Terminal()
    with term.cbreak(), term.hidden_cursor(), term.fullscreen():
        idx = 0
        dirty = True
        while True:
            if dirty:
                outp = render(term, stuff, idx)
                print(outp, end='', flush=True)
            with term.hidden_cursor():
                inp = term.inkey()
            dirty = True
            if inp.code == term.KEY_UP:
                idx -= 1
            elif inp.code == term.KEY_DOWN:
                idx += 1

@click.group(invoke_without_command=True)
@click.option('--b/--no-b', default=False)
@click.pass_context
def cli(ctx, b):
    if ctx.invoked_subcommand is None:
        if b:
            show_tickets()
        else:
            print(get_active_sprint(SES_BOARD))

            print("only sprint")

@cli.command()
@click.argument('issue_id')
def o(issue_id):
    """Open the issue id"""
    webbrowser.open_new(f"https://xilis.atlassian.net/browse/SES-{issue_id}")

if __name__ == '__main__':
    cli()

