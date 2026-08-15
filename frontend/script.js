const STORAGE_KEY = "taskflow_tasks";
const API_BASE_URL = "http://127.0.0.1:8000";
const PROJECT_ID = 1;

const taskForm = document.getElementById("task-form");
const taskTitleInput = document.getElementById("task-title");
const taskDueDateInput = document.getElementById("task-due-date");
const taskPriorityInput = document.getElementById("task-priority");
const titleError = document.getElementById("title-error");
const taskListContainer = document.getElementById("task-list");

let tasks = [];

function loadCachedTasks() {
  const cached = localStorage.getItem(STORAGE_KEY);
  if (cached) {
    try {
      tasks = JSON.parse(cached);
      renderTasks();
    } catch (e) {
      console.error("Failed to parse cached tasks", e);
    }
  }
}

function cacheTasks() {
  localStorage.setItem(STORAGE_KEY, JSON.stringify(tasks));
}

async function fetchTasks() {
  try {
    const response = await fetch(`${API_BASE_URL}/tasks`);
    if (!response.ok) throw new Error("Failed to fetch tasks");
    const data = await response.json();
    tasks = data;
    cacheTasks();
    renderTasks();
  } catch (error) {
    console.error("Error fetching tasks:", error);
  }
}

function renderTasks() {
  taskListContainer.innerHTML = "";

  if (tasks.length === 0) {
    const emptyMsg = document.createElement("p");
    emptyMsg.textContent = "No tasks yet. Add one above!";
    taskListContainer.appendChild(emptyMsg);
    return;
  }

  tasks.forEach((task) => {
    const taskItem = document.createElement("div");
    taskItem.className = "task-item";

    const infoDiv = document.createElement("div");
    infoDiv.className = "task-item-info";

    const titleEl = document.createElement("div");
    titleEl.className = "task-item-title";
    titleEl.textContent = task.title;

    const metaEl = document.createElement("div");
    metaEl.className = "task-item-meta";
    const dueDateText = task.due_date ? `Due: ${task.due_date}` : "No due date";
    metaEl.textContent = dueDateText;

    const priorityEl = document.createElement("span");
    priorityEl.className = `priority-${task.priority}`;
    priorityEl.textContent = ` [${task.priority.toUpperCase()}]`;
    metaEl.appendChild(priorityEl);

    infoDiv.appendChild(titleEl);
    infoDiv.appendChild(metaEl);

    const actionsDiv = document.createElement("div");
    actionsDiv.className = "task-item-actions";

    const statusBtn = document.createElement("button");
    statusBtn.className = task.status === "completed" ? "status-btn status-done" : "status-btn status-pending";
    statusBtn.textContent = task.status === "completed" ? "✓ Done" : "Mark Done";
    statusBtn.addEventListener("click", () => toggleTaskStatus(task.id, task.status));

    const editBtn = document.createElement("button");
    editBtn.className = "edit-btn";
    editBtn.textContent = "Edit";
    editBtn.addEventListener("click", () => editTask(task.id, task.title));

    const deleteBtn = document.createElement("button");
    deleteBtn.className = "delete-btn";
    deleteBtn.textContent = "Delete";
    deleteBtn.addEventListener("click", () => deleteTask(task.id));

    actionsDiv.appendChild(statusBtn);
    actionsDiv.appendChild(editBtn);
    actionsDiv.appendChild(deleteBtn);

    taskItem.appendChild(infoDiv);
    taskItem.appendChild(actionsDiv);

    taskListContainer.appendChild(taskItem);
  });
}

function validateTitle() {
  const value = taskTitleInput.value.trim();
  if (value === "") {
    titleError.textContent = "Task title cannot be empty.";
    return false;
  }
  titleError.textContent = "";
  return true;
}

taskTitleInput.addEventListener("input", validateTitle);

taskForm.addEventListener("submit", async function (event) {
  event.preventDefault();

  if (!validateTitle()) {
    return;
  }

  const newTask = {
    title: taskTitleInput.value.trim(),
    due_date: taskDueDateInput.value.trim(),
    priority: taskPriorityInput.value,
    project_id: PROJECT_ID,
  };

  try {
    const response = await fetch(`${API_BASE_URL}/tasks`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(newTask),
    });

    if (!response.ok) throw new Error("Failed to create task");

    await fetchTasks();
    taskForm.reset();
    taskPriorityInput.value = "medium";
  } catch (error) {
    console.error("Error creating task:", error);
    alert("Failed to add task. Please check the backend is running.");
  }
});

async function toggleTaskStatus(id, currentStatus) {
  const newStatus = currentStatus === "completed" ? "pending" : "completed";

  try {
    const response = await fetch(`${API_BASE_URL}/tasks/${id}`, {
      method: "PUT",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ status: newStatus }),
    });

    if (!response.ok) throw new Error("Failed to update status");

    await fetchTasks();
  } catch (error) {
    console.error("Error updating status:", error);
    alert("Failed to update task status.");
  }
}

async function editTask(id, currentTitle) {
  const newTitle = prompt("Edit task title:", currentTitle);
  if (newTitle === null) return;

  const trimmedTitle = newTitle.trim();
  if (trimmedTitle === "") {
    alert("Task title cannot be empty.");
    return;
  }

  try {
    const response = await fetch(`${API_BASE_URL}/tasks/${id}`, {
      method: "PUT",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ title: trimmedTitle }),
    });

    if (!response.ok) throw new Error("Failed to update task");

    await fetchTasks();
  } catch (error) {
    console.error("Error updating task:", error);
    alert("Failed to update task.");
  }
}

async function deleteTask(id) {
  try {
    const response = await fetch(`${API_BASE_URL}/tasks/${id}`, {
      method: "DELETE",
    });

    if (!response.ok) throw new Error("Failed to delete task");

    await fetchTasks();
  } catch (error) {
    console.error("Error deleting task:", error);
    alert("Failed to delete task.");
  }
}

loadCachedTasks();
fetchTasks();