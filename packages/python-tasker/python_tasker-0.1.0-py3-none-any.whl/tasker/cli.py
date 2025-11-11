import typer
from rich import print
from typing import Optional

from .database import *
from .models import Task, Prio

app = typer.Typer()

@app.command()
def add(task: str, prio: Optional[str] = None):
  """
  Adds a task to your list
  """
  priority: Prio = Prio.MEDIUM
  match prio:
    case "LOW" | "l":
      priority = Prio.LOW
    case "MEDIUM" | "m":
      priority = Prio.MEDIUM
    case "HIGH" | "h":
      priority = Prio.HIGH
    case None:
      priority = Prio.MEDIUM
    case _:
      print("Not a valid priority! [LOW, MEDIUM, HIGH]")
      return
    
  print(f"Added task '{task}' to list with prio {priority.name}")
  add_task(Task(task, priority))

@app.command()
def ls(archived: bool = False):
  """
  List all your tasks
  """
  print_all_tasks(archived)

@app.command()
def archive(task_id: int):
  """
  Mark task as done
  """
  archive_task(task_id)
  print(f"Archived task {task_id}")

@app.command()
def rm(task_id: int):
  """
  Remove task with given id
  """
  remove_task(task_id)
  print(f"Removed task {task_id}")

def main():
  init_db()
  app()

if __name__ == "__main__":
  main()

