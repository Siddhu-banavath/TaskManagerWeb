const apiBase = "";
let token = localStorage.getItem("ttm_token") || "";
let currentUser = null;

const messageEl = document.getElementById("message");
const authSection = document.getElementById("auth-section");
const appSection = document.getElementById("app-section");
const currentUserEl = document.getElementById("current-user");

const setMessage = (msg, isError = false) => {
  messageEl.textContent = msg;
  messageEl.style.color = isError ? "#b91c1c" : "#0f172a";
};

const request = async (path, options = {}) => {
  const headers = { "Content-Type": "application/json", ...(options.headers || {}) };
  if (token) headers.Authorization = `Bearer ${token}`;
  const res = await fetch(`${apiBase}${path}`, { ...options, headers });
  const data = await res.json().catch(() => ({}));
  if (!res.ok) throw new Error(data.detail || "Request failed");
  return data;
};

const updateAuthView = () => {
  const loggedIn = Boolean(token && currentUser);
  authSection.classList.toggle("hidden", loggedIn);
  appSection.classList.toggle("hidden", !loggedIn);
  if (loggedIn) {
    currentUserEl.textContent = `Logged in as ${currentUser.full_name} (${currentUser.global_role}) - User ID: ${currentUser.id}`;
  }
};

const loadCurrentUser = async () => {
  if (!token) return;
  try {
    currentUser = await request("/api/auth/me");
    updateAuthView();
    await Promise.all([loadSummary(), loadProjects(), loadMyTasks()]);
  } catch {
    token = "";
    currentUser = null;
    localStorage.removeItem("ttm_token");
    updateAuthView();
  }
};

const loadSummary = async () => {
  const summary = await request("/api/dashboard/summary");
  Object.entries(summary).forEach(([key, value]) => {
    const el = document.getElementById(key);
    if (el) el.textContent = value;
  });
};

const loadProjects = async () => {
  const projects = await request("/api/projects");
  const list = document.getElementById("project-list");
  list.innerHTML = projects
    .map((p) => `<li>#${p.id} - ${p.name} (${p.description || "No description"})</li>`)
    .join("");
};

const loadMyTasks = async () => {
  const tasks = await request("/api/tasks/my");
  const list = document.getElementById("task-list");
  list.innerHTML = tasks
    .map((t) => `<li>#${t.id} - ${t.title} [${t.status}] (due: ${t.due_date || "none"})</li>`)
    .join("");
};

document.getElementById("signup-form").addEventListener("submit", async (e) => {
  e.preventDefault();
  const form = new FormData(e.target);
  try {
    const data = await request("/api/auth/signup", {
      method: "POST",
      body: JSON.stringify(Object.fromEntries(form.entries())),
    });
    token = data.access_token;
    currentUser = data.user;
    localStorage.setItem("ttm_token", token);
    updateAuthView();
    await Promise.all([loadSummary(), loadProjects(), loadMyTasks()]);
    setMessage("Signup successful.");
    e.target.reset();
  } catch (err) {
    setMessage(err.message, true);
  }
});

document.getElementById("login-form").addEventListener("submit", async (e) => {
  e.preventDefault();
  const form = new FormData(e.target);
  try {
    const data = await request("/api/auth/login", {
      method: "POST",
      body: JSON.stringify(Object.fromEntries(form.entries())),
    });
    token = data.access_token;
    currentUser = data.user;
    localStorage.setItem("ttm_token", token);
    updateAuthView();
    await Promise.all([loadSummary(), loadProjects(), loadMyTasks()]);
    setMessage("Login successful.");
    e.target.reset();
  } catch (err) {
    setMessage(err.message, true);
  }
});

document.getElementById("logout-btn").addEventListener("click", () => {
  token = "";
  currentUser = null;
  localStorage.removeItem("ttm_token");
  updateAuthView();
  setMessage("Logged out.");
});

document.getElementById("project-form").addEventListener("submit", async (e) => {
  e.preventDefault();
  const form = new FormData(e.target);
  try {
    await request("/api/projects", { method: "POST", body: JSON.stringify(Object.fromEntries(form.entries())) });
    await Promise.all([loadSummary(), loadProjects()]);
    setMessage("Project created.");
    e.target.reset();
  } catch (err) {
    setMessage(err.message, true);
  }
});

document.getElementById("member-form").addEventListener("submit", async (e) => {
  e.preventDefault();
  const form = Object.fromEntries(new FormData(e.target).entries());
  const projectId = form.project_id;
  delete form.project_id;
  form.user_id = Number(form.user_id);
  try {
    await request(`/api/projects/${projectId}/members`, { method: "POST", body: JSON.stringify(form) });
    setMessage("Member updated.");
    e.target.reset();
  } catch (err) {
    setMessage(err.message, true);
  }
});

document.getElementById("task-form").addEventListener("submit", async (e) => {
  e.preventDefault();
  const form = Object.fromEntries(new FormData(e.target).entries());
  const projectId = form.project_id;
  delete form.project_id;
  form.assignee_id = form.assignee_id ? Number(form.assignee_id) : null;
  form.due_date = form.due_date || null;
  try {
    await request(`/api/projects/${projectId}/tasks`, { method: "POST", body: JSON.stringify(form) });
    await Promise.all([loadSummary(), loadMyTasks()]);
    setMessage("Task created.");
    e.target.reset();
  } catch (err) {
    setMessage(err.message, true);
  }
});

document.getElementById("status-form").addEventListener("submit", async (e) => {
  e.preventDefault();
  const form = Object.fromEntries(new FormData(e.target).entries());
  try {
    await request(`/api/tasks/${form.task_id}`, {
      method: "PATCH",
      body: JSON.stringify({ status: form.status }),
    });
    await Promise.all([loadSummary(), loadMyTasks()]);
    setMessage("Task status updated.");
    e.target.reset();
  } catch (err) {
    setMessage(err.message, true);
  }
});

document.getElementById("refresh-projects").addEventListener("click", async () => {
  try {
    await loadProjects();
    setMessage("Projects refreshed.");
  } catch (err) {
    setMessage(err.message, true);
  }
});

document.getElementById("refresh-tasks").addEventListener("click", async () => {
  try {
    await loadMyTasks();
    setMessage("Tasks refreshed.");
  } catch (err) {
    setMessage(err.message, true);
  }
});

loadCurrentUser();
updateAuthView();

