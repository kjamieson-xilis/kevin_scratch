import pprint

from blessed import Terminal
import click
import jira
from rich.console import Console
from rich.table import Table
from rich.style import Style

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
PROJECT = 'SES'
USERNAME = 'kevin.jamieson@xilis.net'

DONE_ROW = Style(strike=True)

def get_active_sprint(board_id):
    gh = jira.client.GreenHopper(OPTIONS)
    sprints = gh.sprints(board_id)
    active_sprint = [x for x in sprints if x.state == 'active']
    if active_sprint:
        return active_sprint[0]
    else:
        return None

def move_issue(issue_id):
    j = jira.JIRA(OPTIONS)
    issue = j.issue(issue_id)
    print(f'{issue_id} CURRENT STATUS: {issue.fields.status}')
    available_transitions = j.transitions(issue_id)
    print(f'Available Transitions:')
    for index, t in enumerate(available_transitions):
        print(f"{index}. - {t['name']}")
    choice = input('Choice? ')
    try:
        transition = available_transitions[int(choice)]
        result = j.transition_issue(issue, transition['id'])
    except Exception:
        print('Invalid selection, aborting')

def get_issue_description(issue_id):
    j = jira.JIRA(OPTIONS)
    desc = j.issue(issue_id).fields.description
    return desc

def get_issue_comments(issue_id):
    j = jira.JIRA(OPTIONS)
    comments = j.comments(issue_id)
    return comments

def get_sprint_issues(sprint_id):
    j = jira.JIRA(OPTIONS)
    JQL = f'sprint = {sprint_id} and assignee in (currentUser())'
    results = j.search_issues(JQL, expand="Names")
    return [x for x in results]

def get_tickets():
    j = jira.JIRA(OPTIONS)
    JQL = f'statusCategory != "Done" AND assignee in (currentUser()) order by priority'
    results = j.search_issues(JQL, expand="Names")
    infra_tickets = []
    for entry in results:
            infra_tickets.append(entry)
    return infra_tickets

def add_comment(issue_id, comment_text):
    j = jira.JIRA(OPTIONS)
    j.add_comment(issue_id, comment_text)

def show_comments(ticket_id):
    desc = get_issue_description(ticket_id)
    comments = get_issue_comments(ticket_id)
    console = Console()
    desc_table = Table(show_header=True, header_style="bold yellow")
    desc_table.add_column("Description")
    desc_table.add_row(desc)
    console.print(desc_table)

    infra_table = Table(show_header=True, header_style="bold green")
    infra_table.add_column("Date")
    infra_table.add_column("Author")
    infra_table.add_column("Comment")
    for comment in comments:
        infra_table.add_row(comment.created, comment.author.displayName, comment.body)
    console.print(infra_table)


def show_tickets(ticket_list):
    infra = ticket_list
    console = Console()
    infra_table = Table(show_header=True, header_style="bold green")
    infra_table.add_column("Key")
    infra_table.add_column("Summary")
    infra_table.add_column("Status")
    infra_table.add_column("Priority")
    for x in infra:
        style = None
        if x.fields.status.name == 'DONE':
            style = DONE_ROW
        infra_table.add_row(x.key, x.fields.summary, x.fields.status.name, x.fields.priority.name, style=style)

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
    """Show current sprint tickets, pass --b to show backlog"""
    if ctx.invoked_subcommand is None:
        if b:
            show_tickets(get_tickets())
        else:
            active_sprint = get_active_sprint(SES_BOARD)
            show_tickets(get_sprint_issues(active_sprint.id))

@cli.command()
@click.argument('issue_id')
@click.option('--a')
def c(issue_id, a):
    """Show comments on issue"""
    if a:
        add_comment(issue_id, a)
    show_comments(issue_id)

@cli.command()
@click.argument('issue_id')
def m(issue_id):
    """Move (transition) issue status"""
    move_issue(issue_id)

@cli.command()
def n():
    """Create new issue."""
    j = jira.JIRA(OPTIONS)
    issue_type_fullname = {'b': 'Bug', 't': 'Task', 's': 'Story'}
    issue_type = input("Type? t=Task, b=Bug, s=Story ").lower()
    add_to_sprint = input("Add to current sprint? y/n: ").lower()
    print(f"Creating issue type {issue_type_fullname[issue_type]}")
    summary = input("Summary: ")
    description = input("Description: ")
    new_issue = j.create_issue(project=PROJECT, summary=summary, description=description, issuetype={'name': issue_type_fullname[issue_type]})
    j.assign_issue(new_issue, USERNAME)
    print(f"New issue created, {new_issue}")
    if add_to_sprint == 'y':
        active_sprint = get_active_sprint(SES_BOARD)
        j.add_issues_to_sprint(sprint_id=active_sprint.id, issue_keys=[new_issue.key])


@cli.command()
@click.argument('issue_id')
def o(issue_id):
    """Open the issue id in a web browser"""
    webbrowser.open_new(f"https://xilis.atlassian.net/browse/{issue_id}")

if __name__ == '__main__':
    cli()
