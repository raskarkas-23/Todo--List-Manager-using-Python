import os

FILE_NAME = "tasks.txt"

def load_tasks():
    tasks = []
    if os.path.exists(FILE_NAME):
        with open(FILE_NAME, "r") as file:
            for line in file:
                name, status = line.strip().split("|")
                tasks.append({"task": name, "status": status})
    return tasks

def save_tasks(tasks):
    with open(FILE_NAME, "w") as file:
        for task in tasks:
            file.write(f"{task['task']}|{task['status']}\n")

def add_task(tasks):
    task_name = input("Enter task name: ")
    tasks.append({"task": task_name, "status": "Pending"})
    save_tasks(tasks)
    print("Task added successfully!")

def view_tasks(tasks):
    if not tasks:
        print("No tasks available.")
        return
    for i, task in enumerate(tasks, start=1):
        print(f"{i}. {task['task']} - {task['status']}")

def update_task(tasks):
    view_tasks(tasks)
    try:
        index = int(input("Enter task number to update: ")) - 1
        if tasks[index]["status"] == "Pending":
            tasks[index]["status"] = "Completed"
        else:
            tasks[index]["status"] = "Pending"
        save_tasks(tasks)
        print("Task status updated!")
    except (IndexError, ValueError):
        print("Invalid selection!")

def delete_task(tasks):
    view_tasks(tasks)
    try:
        index = int(input("Enter task number to delete: ")) - 1
        removed = tasks.pop(index)
        save_tasks(tasks)
        print(f"Task '{removed['task']}' deleted!")
    except (IndexError, ValueError):
        print("Invalid selection!")

def main():
    tasks = load_tasks()
    while True:
        print("\n--- To-Do List Manager ---")
        print("1. Add Task")
        print("2. View Tasks")
        print("3. Update Task Status")
        print("4. Delete Task")
        print("5. Exit")

        choice = input("Enter your choice: ")

        if choice == "1":
            add_task(tasks)
        elif choice == "2":
            view_tasks(tasks)
        elif choice == "3":
            update_task(tasks)
        elif choice == "4":
            delete_task(tasks)
        elif choice == "5":
            print("Exiting program. Goodbye!")
            break
        else:
            print(" Invalid choice. Try again!")

if __name__ == "__main__":
    main()
