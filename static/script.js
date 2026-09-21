const API = "/api/notes";

const titleInput   = document.getElementById("title");
const contentInput = document.getElementById("content");
const saveBtn      = document.getElementById("save-btn");
const statusEl     = document.getElementById("status");
const notesList    = document.getElementById("notes-list");
const countEl      = document.getElementById("count");

document.addEventListener("DOMContentLoaded", loadNotes);

saveBtn.addEventListener("click", async () => {
  const title = titleInput.value.trim();
  const content = contentInput.value.trim();

  if (!title || !content) {
    showStatus("Please fill in both fields.", "error");
    return;
  }

  saveBtn.disabled = true;
  saveBtn.querySelector(".btn-text").textContent = "Saving...";

  try {
    const res = await fetch(API, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ title, content })
    });
    if (!res.ok) throw new Error();
    titleInput.value = "";
    contentInput.value = "";
    showStatus("Note saved! ✅", "success");
    await loadNotes();
  } catch {
    showStatus("Something went wrong.", "error");
  } finally {
    saveBtn.disabled = false;
    saveBtn.querySelector(".btn-text").textContent = "Save Note";
  }
});

async function deleteNote(id) {
  if (!confirm("Delete this note?")) return;
  await fetch(`${API}/${id}`, { method: "DELETE" });
  await loadNotes();
}

async function loadNotes() {
  try {
    const res = await fetch(API);
    const notes = await res.json();
    countEl.textContent = notes.length;

    if (notes.length === 0) {
      notesList.innerHTML = `<p class="empty">No notes yet. Add one above! ☝️</p>`;
      return;
    }

    notesList.innerHTML = notes.map(n => `
      <div class="note-card">
        <h3>${escapeHtml(n.title)}</h3>
        <p>${escapeHtml(n.content)}</p>
        <div class="date">${new Date(n.created_at).toLocaleString()}</div>
        <button class="delete-btn" onclick="deleteNote(${n.id})">🗑️ Delete</button>
      </div>
    `).join("");
  } catch {
    notesList.innerHTML = `<p class="empty">Could not load notes. 😢</p>`;
  }
}

function showStatus(msg, type) {
  statusEl.textContent = msg;
  statusEl.className = "status " + type;
  setTimeout(() => { statusEl.textContent = ""; statusEl.className = "status"; }, 3000);
}

function escapeHtml(str) {
  const div = document.createElement("div");
  div.textContent = str;
  return div.innerHTML;
}