import datetime
import calendar
import sys
import zulip
from decouple import config
from github import Github
from utils import construct_meeting_message, get_table_open_issues, get_table_zulip_members, construct_issue_message, \
    get_assigned_users, construct_assigned_issues, get_table_ignored_assignees, get_zulip_id_from_assignee, get_names
from rich.traceback import install
install(show_locals=True)
from rich.console import Console
console = Console()

today = datetime.datetime.now()
month = calendar.monthcalendar(today.year, today.month)
last_sunday = max(month[-1][calendar.SUNDAY], month[-2][calendar.SUNDAY])

# Pass the path to your zuliprc file here.
client = zulip.Client(email="reminder-bot@mongulu.zulipchat.com", api_key=config('API_KEY'),
                      site="https://mongulu.zulipchat.com")

token = config("GH_TOKEN")
g = Github(token,verify=False)

try:

    if config("REMINDER_TYPE", default="") == "ISSUES":

        t1 = get_table_open_issues(g)
        t1.present()
        t2 = get_table_zulip_members(client)
        t2.present()

        names = get_names(t2)
        assignees, ignored_assignees = get_assigned_users(t1, names)

        for assignee in assignees:
            message = construct_issue_message([x for x in t1.where(lambda o: assignee in o.Assignees)])
            id = get_zulip_id_from_assignee(t2, names, assignee)
            request = {"type": "private", "to": [id], "content": f" {message}"}
            result = client.send_message(request)
            print(f"👉 {result}")


        t3 = get_table_ignored_assignees(ignored_assignees)
        messages = construct_assigned_issues(t3.as_markdown())
        for message in messages:
            request = {"type": "private", "to": [470841], "content": f"{message}"}
            result = client.send_message(request)
            print(f"👉 {result}")

    else:

        message = construct_meeting_message(today, last_sunday)
        if message != "":
            request = {"type": "stream", "to": "general", "topic": "meeting", "content": " {} ".format(message)}
            result = client.send_message(request)
            print(f"👉 {result}")


except Exception:
    console.print_exception(show_locals=True)
    sys.exit(-1)



