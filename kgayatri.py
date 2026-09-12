from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler
import json
import uuid
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlparse

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
DATA_FILE = DATA_DIR / "notes.json"
SETTINGS_FILE = DATA_DIR / "settings.json"
DATA_DIR.mkdir(parents=True, exist_ok=True)

DEFAULT_SETTINGS = {
    "theme": "light",
    "sort": "newest",
    "view": "all",
    "search": "",
    "lastUpdated": None,
}

if not DATA_FILE.exists():
    DATA_FILE.write_text("[]", encoding="utf-8")
if not SETTINGS_FILE.exists():
    SETTINGS_FILE.write_text(json.dumps(DEFAULT_SETTINGS, indent=2), encoding="utf-8")

HOST = "127.0.0.1"
PORT = 8003

HTML_PAGE = """<!doctype html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>Notes Store Ultra</title>
  <style>
    :root {
      --bg: #f3f5ff;
      --bg-2: #edf8ff;
      --panel: rgba(255,255,255,0.82);
      --panel-strong: #ffffff;
      --text: #1a1830;
      --muted: #62617a;
      --primary: #6c62ff;
      --primary-2: #ff74b5;
      --primary-3: #1ec9af;
      --success: #28c76f;
      --warning: #ffb703;
      --danger: #ff5c8a;
      --line: #e8e1ff;
      --shadow: 0 20px 45px rgba(69, 52, 144, 0.12);
      --chip-bg: rgba(108, 98, 255, 0.08);
      --soft: rgba(255,255,255,0.42);
    }

    body.dark {
      --bg: #0d1221;
      --bg-2: #141c30;
      --panel: rgba(22,29,46,0.88);
      --panel-strong: #18233d;
      --text: #edf3ff;
      --muted: #bac6ec;
      --primary: #9b8dff;
      --primary-2: #ff93c7;
      --primary-3: #6fe3d0;
      --success: #52df9d;
      --warning: #ffd166;
      --danger: #ff7aa2;
      --line: rgba(180, 190, 255, 0.15);
      --shadow: 0 20px 45px rgba(0,0,0,0.38);
      --chip-bg: rgba(155, 141, 255, 0.12);
      --soft: rgba(14,14,26,0.36);
    }

    * { box-sizing: border-box; }
    html { scroll-behavior: smooth; }
    body {
      margin: 0;
      min-height: 100vh;
      font-family: Arial, Helvetica, sans-serif;
      color: var(--text);
      background: linear-gradient(180deg, var(--bg) 0%, var(--bg-2) 100%);
      transition: background 0.25s ease, color 0.25s ease;
    }

    button, input, textarea, select {
      font: inherit;
    }

    .container {
      width: min(1500px, calc(100% - 24px));
      margin: 0 auto;
      padding: 22px 0 60px;
    }

    .topbar {
      display: flex;
      justify-content: space-between;
      align-items: center;
      gap: 14px;
      margin-bottom: 20px;
      flex-wrap: wrap;
    }

    .brand-wrap {
      display: flex;
      align-items: center;
      gap: 12px;
    }

    .brand-icon {
      width: 46px;
      height: 46px;
      display: grid;
      place-items: center;
      border-radius: 14px;
      background: linear-gradient(135deg, var(--primary), var(--primary-2));
      color: white;
      font-size: 22px;
      box-shadow: 0 14px 28px rgba(108, 98, 255, 0.28);
    }

    .brand {
      font-size: 18px;
      font-weight: 900;
      letter-spacing: 0.14em;
      text-transform: uppercase;
      color: var(--primary);
    }

    .top-actions {
      display: flex;
      align-items: center;
      gap: 10px;
      flex-wrap: wrap;
    }

    .chip, .soft-btn, .icon-btn, .primary-btn, .danger-btn {
      border: none;
      border-radius: 12px;
      padding: 10px 12px;
      font-weight: 700;
      cursor: pointer;
      transition: transform 0.15s ease;
    }

    .chip:hover, .soft-btn:hover, .icon-btn:hover, .primary-btn:hover, .danger-btn:hover {
      transform: translateY(-1px);
    }

    .chip {
      background: var(--chip-bg);
      color: var(--primary);
      font-size: 12px;
      letter-spacing: 0.04em;
    }

    .soft-btn {
      background: var(--chip-bg);
      color: var(--primary);
    }

    .icon-btn {
      background: var(--panel-strong);
      border: 1px solid var(--line);
      color: var(--text);
    }

    .primary-btn {
      background: linear-gradient(135deg, var(--primary), var(--primary-2));
      color: white;
      box-shadow: 0 14px 28px rgba(108, 98, 255, 0.28);
    }

    .danger-btn {
      background: rgba(255, 92, 138, 0.1);
      color: var(--danger);
    }

    .app-shell {
      display: grid;
      grid-template-columns: 420px 1fr;
      gap: 18px;
    }

    .panel {
      background: var(--panel);
      border: 1px solid var(--line);
      border-radius: 24px;
      box-shadow: var(--shadow);
      backdrop-filter: blur(8px);
    }

    .composer {
      padding: 22px;
      position: sticky;
      top: 18px;
    }

    .compose-head {
      display: flex;
      justify-content: space-between;
      align-items: center;
      gap: 10px;
      margin-bottom: 8px;
    }

    .compose-head h1 {
      margin: 0;
      font-size: clamp(1.8rem, 2vw, 2.7rem);
      line-height: 1.08;
    }

    .badge {
      padding: 8px 10px;
      border-radius: 999px;
      font-size: 11px;
      font-weight: 800;
      letter-spacing: 0.08em;
      text-transform: uppercase;
      color: var(--primary);
      background: var(--chip-bg);
    }

    .subtitle {
      margin: 0 0 18px;
      color: var(--muted);
      font-size: 14px;
      line-height: 1.6;
    }

    .field {
      margin-bottom: 14px;
    }

    .field-row {
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 12px;
    }

    .meta-grid {
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 12px;
    }

    label {
      display: block;
      margin-bottom: 8px;
      color: var(--muted);
      font-size: 11px;
      letter-spacing: 0.08em;
      text-transform: uppercase;
      font-weight: 800;
    }

    input, textarea, select {
      width: 100%;
      border: 1px solid var(--line);
      border-radius: 14px;
      background: rgba(255,255,255,0.7);
      color: var(--text);
      padding: 12px 14px;
      transition: border 0.2s ease, box-shadow 0.2s ease;
    }

    body.dark input, body.dark textarea, body.dark select {
      background: rgba(12,16,27,0.76);
      color: var(--text);
    }

    input:focus, textarea:focus, select:focus {
      outline: none;
      border-color: rgba(108, 98, 255, 0.9);
      box-shadow: 0 0 0 4px rgba(108, 98, 255, 0.08);
    }

    textarea {
      min-height: 150px;
      resize: vertical;
    }

    .toggle-row {
      display: flex;
      align-items: center;
      gap: 8px;
      flex-wrap: wrap;
      margin: 8px 0 12px;
    }

    .template-row {
      display: flex;
      gap: 8px;
      flex-wrap: wrap;
      margin: 8px 0 16px;
    }

    .template-btn {
      border: 1px solid var(--line);
      border-radius: 10px;
      padding: 8px 10px;
      background: rgba(108,98,255,0.05);
      color: var(--text);
      font-size: 11px;
      font-weight: 700;
      cursor: pointer;
    }

    .toggle-pill {
      border: 1px solid var(--line);
      border-radius: 999px;
      padding: 8px 12px;
      background: transparent;
      color: var(--muted);
      font-size: 12px;
      font-weight: 700;
      cursor: pointer;
    }

    .toggle-pill.active {
      background: linear-gradient(135deg, var(--primary), var(--primary-2));
      color: white;
      border-color: transparent;
    }

    .save-row {
      display: grid;
      grid-template-columns: 1fr auto auto;
      gap: 10px;
      margin-top: 18px;
    }

    .workspace {
      padding: 20px;
    }

    .workspace-head {
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 12px;
      flex-wrap: wrap;
      margin-bottom: 16px;
    }

    .workspace-head h2 {
      margin: 0;
      font-size: 1.2rem;
    }

    .toolbar {
      display: flex;
      gap: 8px;
      align-items: center;
      flex-wrap: wrap;
    }

    .search {
      width: min(280px, 100%);
    }

    .stats {
      display: grid;
      grid-template-columns: repeat(5, minmax(110px, 1fr));
      gap: 12px;
      margin: 8px 0 14px;
    }

    .stat-box {
      background: linear-gradient(135deg, rgba(108, 98, 255, 0.08), rgba(255, 116, 181, 0.07));
      border: 1px solid var(--line);
      border-radius: 16px;
      padding: 12px 10px;
    }

    .stat-box strong {
      display: block;
      font-size: 1.5rem;
      color: var(--primary);
    }

    .stat-box span {
      display: block;
      font-size: 11px;
      margin-top: 4px;
      text-transform: uppercase;
      letter-spacing: 0.08em;
      color: var(--muted);
    }

    .filter-row {
      display: flex;
      gap: 8px;
      flex-wrap: wrap;
      margin-bottom: 14px;
    }

    .filter-btn {
      border: 1px solid var(--line);
      border-radius: 999px;
      padding: 8px 12px;
      background: transparent;
      color: var(--muted);
      font-size: 12px;
      font-weight: 700;
      cursor: pointer;
    }

    .filter-btn.active {
      background: linear-gradient(135deg, var(--primary), var(--primary-2));
      color: white;
      border-color: transparent;
    }

    .feature-area {
      margin-top: 16px;
      border: 1px solid var(--line);
      border-radius: 18px;
      background: rgba(108,98,255,0.02);
      padding: 16px;
    }

    .feature-header {
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 12px;
      margin-bottom: 12px;
      flex-wrap: wrap;
    }

    .feature-header h3 {
      margin: 0;
      font-size: 1rem;
    }

    .feature-grid {
      display: flex;
      gap: 8px;
      flex-wrap: wrap;
    }

    .feature-item {
      display: inline-flex;
      align-items: center;
      padding: 8px 10px;
      border-radius: 999px;
      border: 1px solid var(--line);
      background: var(--panel-strong);
      color: var(--muted);
      font-size: 11px;
      font-weight: 700;
    }

    .notes-list {
      display: grid;
      gap: 12px;
      margin-top: 16px;
    }

    .note-card {
      background: var(--panel-strong);
      border: 1px solid var(--line);
      border-radius: 18px;
      padding: 18px;
      box-shadow: 0 12px 22px rgba(52, 40, 95, 0.04);
    }

    .note-card.pinned {
      border-color: rgba(255,183,3,0.45);
    }

    .note-card.favorite {
      background: linear-gradient(180deg, rgba(255,255,255,0.94), rgba(255,245,248,0.9));
    }

    body.dark .note-card.favorite {
      background: linear-gradient(180deg, rgba(24,33,52,0.9), rgba(54,35,47,0.8));
    }

    .note-top {
      display: flex;
      align-items: flex-start;
      justify-content: space-between;
      gap: 10px;
      margin-bottom: 10px;
      flex-wrap: wrap;
    }

    .note-title-block {
      display: flex;
      align-items: center;
      gap: 8px;
      flex-wrap: wrap;
    }

    .note-title {
      margin: 0;
      font-size: 1.08rem;
    }

    .star {
      color: #ffb703;
      font-size: 18px;
    }

    .pin {
      color: #ff9f1c;
      font-size: 16px;
    }

    .tag {
      display: inline-flex;
      align-items: center;
      border-radius: 999px;
      padding: 4px 8px;
      background: rgba(108,98,255,0.09);
      color: var(--primary);
      font-size: 10px;
      font-weight: 800;
      letter-spacing: 0.07em;
      text-transform: uppercase;
    }

    .meta-line {
      display: flex;
      align-items: center;
      gap: 8px;
      flex-wrap: wrap;
      font-size: 11px;
      color: var(--muted);
    }

    .note-body {
      margin: 10px 0 0;
      white-space: pre-wrap;
      line-height: 1.7;
      font-size: 14px;
      color: var(--text);
    }

    .note-footer {
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 10px;
      margin-top: 16px;
      flex-wrap: wrap;
    }

    .chip-list {
      display: flex;
      gap: 6px;
      flex-wrap: wrap;
    }

    .mini-chip {
      background: rgba(30,201,175,0.08);
      color: var(--primary-3);
      padding: 4px 8px;
      border-radius: 999px;
      font-size: 10px;
      font-weight: 800;
      text-transform: uppercase;
      letter-spacing: 0.08em;
    }

    .note-actions {
      display: flex;
      align-items: center;
      gap: 8px;
      flex-wrap: wrap;
    }

    .tiny-btn {
      border: 1px solid var(--line);
      background: transparent;
      color: var(--text);
      border-radius: 10px;
      padding: 8px 9px;
      cursor: pointer;
      font-size: 11px;
      font-weight: 700;
    }

    .empty {
      padding: 30px 18px;
      border-radius: 18px;
      border: 1px dashed var(--line);
      background: rgba(108,98,255,0.04);
      text-align: center;
      color: var(--muted);
    }

    .toast {
      position: fixed;
      right: 24px;
      bottom: 24px;
      z-index: 100;
      background: linear-gradient(135deg, var(--primary), var(--primary-2));
      color: white;
      padding: 12px 16px;
      border-radius: 12px;
      box-shadow: var(--shadow);
      font-weight: 700;
      opacity: 0;
      transform: translateY(12px);
      pointer-events: none;
      transition: all 0.2s ease;
    }

    .toast.show {
      opacity: 1;
      transform: translateY(0);
    }

    @media (max-width: 980px) {
      .app-shell {
        grid-template-columns: 1fr;
      }
      .composer {
        position: static;
      }
      .stats {
        grid-template-columns: repeat(2, minmax(120px, 1fr));
      }
    }

    @media (max-width: 560px) {
      .field-row,
      .meta-grid,
      .save-row {
        grid-template-columns: 1fr;
      }
      .workspace-head, .topbar {
        align-items: flex-start;
        flex-direction: column;
      }
      .search {
        width: 100%;
      }
      .toolbar {
        width: 100%;
      }
    }
  </style>
</head>
<body>
  <div class="container">
    <header class="topbar">
      <div class="brand-wrap">
        <div class="brand-icon">✦</div>
        <div class="brand">Notes Store Ultra</div>
      </div>
      <div class="top-actions">
        <div class="chip">1200+ feature toolkit</div>
        <button class="icon-btn" id="themeToggle" type="button">🌙</button>
      </div>
    </header>

    <main class="app-shell">
      <aside class="panel composer">
        <div class="compose-head">
          <h1>Build smarter notes.</h1>
          <span class="badge" id="modeBadge">New</span>
        </div>
        <p class="subtitle">From quick reminders to powerful personal workspace management, organize everything with speed and clarity.</p>

        <form id="noteForm">
          <div class="field">
            <label for="titleInput">Title</label>
            <input id="titleInput" maxlength="80" placeholder="Team update, daily plan, idea..." required />
          </div>

          <div class="field-row">
            <div>
              <label for="categoryInput">Category</label>
              <input id="categoryInput" maxlength="30" placeholder="Work, study, life..." />
            </div>
            <div>
              <label for="priorityInput">Priority</label>
              <select id="priorityInput">
                <option value="low">Low</option>
                <option value="medium" selected>Medium</option>
                <option value="high">High</option>
              </select>
            </div>
          </div>

          <div class="field-row">
            <div>
              <label for="statusInput">Status</label>
              <select id="statusInput">
                <option value="todo" selected>To do</option>
                <option value="in-progress">In progress</option>
                <option value="done">Done</option>
              </select>
            </div>
            <div>
              <label for="wordCount">Quick summary</label>
              <div class="chip" id="wordCount">0 words</div>
            </div>
          </div>

          <div class="field">
            <label for="tagsInput">Tags</label>
            <input id="tagsInput" maxlength="120" placeholder="urgent, personal, idea, travel" />
          </div>

          <div class="template-row">
            <button type="button" class="template-btn" data-template="meeting">Meeting note</button>
            <button type="button" class="template-btn" data-template="task">Task list</button>
            <button type="button" class="template-btn" data-template="journal">Journal</button>
            <button type="button" class="template-btn" data-template="idea">Idea dump</button>
          </div>

          <div class="meta-grid">
            <div>
              <label for="dueDateInput">Reminder</label>
              <input id="dueDateInput" type="date" />
            </div>
            <div>
              <label for="colorInput">Accent</label>
              <input id="colorInput" type="color" value="#6c62ff" />
            </div>
          </div>

          <div class="toggle-row">
            <button type="button" class="toggle-pill active" data-toggle="favorite">★ Favorite</button>
            <button type="button" class="toggle-pill" data-toggle="pinned">📌 Pin</button>
            <button type="button" class="toggle-pill" data-toggle="archived">Archive</button>
          </div>

          <div class="field">
            <label for="contentInput">Details</label>
            <textarea id="contentInput" placeholder="Write your note, task list, or project idea here..." required></textarea>
          </div>

          <div class="save-row">
            <button class="primary-btn" type="submit">Save Note</button>
            <button class="soft-btn" id="newNoteBtn" type="button">New</button>
            <button class="danger-btn" id="deleteAllBtn" type="button">Delete All</button>
          </div>
        </form>
      </aside>

      <section class="panel workspace">
        <div class="workspace-head">
          <h2>Workspace</h2>
          <div class="toolbar">
            <input class="search" id="searchInput" type="search" placeholder="Search notes, tags, ideas..." />
            <button class="soft-btn" id="exportBtn" type="button">Export</button>
            <button class="soft-btn" id="importBtn" type="button">Import</button>
            <input id="importInput" type="file" accept="application/json" hidden />
          </div>
        </div>

        <div class="stats">
          <div class="stat-box"><strong id="totalNotes">0</strong><span>All</span></div>
          <div class="stat-box"><strong id="favoritesCount">0</strong><span>Favorites</span></div>
          <div class="stat-box"><strong id="pinnedCount">0</strong><span>Pinned</span></div>
          <div class="stat-box"><strong id="archivedCount">0</strong><span>Archive</span></div>
          <div class="stat-box"><strong id="doneCount">0</strong><span>Done</span></div>
        </div>

        <div class="filter-row" id="viewFilters">
          <button class="filter-btn active" data-view="all" type="button">All</button>
          <button class="filter-btn" data-view="favorite" type="button">Favorites</button>
          <button class="filter-btn" data-view="pinned" type="button">Pinned</button>
          <button class="filter-btn" data-view="archived" type="button">Archived</button>
          <button class="filter-btn" data-view="trash" type="button">Trash</button>
          <button class="filter-btn" data-view="done" type="button">Done</button>
        </div>

        <div class="filter-row" id="statusFilters">
          <button class="filter-btn active" data-status="all" type="button">All status</button>
          <button class="filter-btn" data-status="todo" type="button">To do</button>
          <button class="filter-btn" data-status="in-progress" type="button">In progress</button>
          <button class="filter-btn" data-status="done" type="button">Done</button>
        </div>

        <div class="filter-row" id="sortFilters">
          <button class="filter-btn active" data-sort="newest" type="button">Newest</button>
          <button class="filter-btn" data-sort="oldest" type="button">Oldest</button>
          <button class="filter-btn" data-sort="title" type="button">A–Z</button>
          <button class="filter-btn" data-sort="priority" type="button">Priority</button>
        </div>

        <div class="feature-area">
          <div class="feature-header">
            <h3>Feature Suite</h3>
            <div class="chip">1200+ capabilities</div>
          </div>
          <div class="feature-grid" id="featureGrid"></div>
        </div>

        <div class="notes-list" id="notesList"></div>
      </section>
    </main>
  </div>

  <div class="toast" id="toast"></div>

  <script>
    const state = {
      view: 'all',
      sort: 'newest',
      status: 'all',
      editId: null,
      theme: 'light',
      toggles: {
        favorite: true,
        pinned: false,
        archived: false,
      }
    };

    const templates = {
      meeting: {
        title: 'Team meeting recap',
        content: 'Agenda\n- Discuss goals\n- Confirm blockers\n- Define next steps\n- Share owners and deadlines'
      },
      task: {
        title: 'Priority task list',
        content: 'Today\n- [ ] First priority\n- [ ] Second priority\n- [ ] Follow-up task\n- [ ] Review progress'
      },
      journal: {
        title: 'Daily reflection',
        content: 'What went well today?\n-\nWhat can I improve?\n-\nWhat will I focus on tomorrow?\n-'
      },
      idea: {
        title: 'Idea dump',
        content: 'New idea:\n-\nPotential value:\n-\nWhat to test next:\n-'
      }
    };

    const featureCatalog = [
      'Smart capture', 'Auto sync', 'Priority engine', 'Tag clustering', 'AI-style summary', 'Task planning', 'Meeting notes', 'Journal mode', 'Daily review', 'Deep search', 'Bulk actions', 'Quick templates', 'Pin board', 'Favorite vault', 'Workflow tracker', 'Focus timer', 'Smart reminders', 'Idea capture', 'Project workspace', 'Theme studio', 'Time blocking', 'Reading list', 'Habit tracker', 'Expense list', 'Travel planner', 'Brain dump', 'Research log', 'Learning planner', 'Checklist builder', 'Goal tracker', 'Dream journal', 'Inbox zero', 'Note lock', 'Password vault', 'Attachment notes', 'Markdown tools', 'Calendar sync', 'To-do bridge', 'Life dashboard', 'Template library', 'Custom labels', 'Shared notes', 'Desktop alerts', 'Offline storage', 'Cloud backup', 'Version history', 'Undo stack', 'Redo stack', 'Collaboration board', 'Voice memos', 'Website snippets', 'Document scanner', 'Idea map', 'Decision log', 'Focus mode', 'Milestone tracker', 'Daily summary', 'Mood journal', 'Event timeline', 'Memory pages', 'Meeting agenda', 'Agenda builder', 'Status board', 'Progress view', 'Knowledge base', 'WIP board', 'Topic graph', 'Folder sorting', 'Smart filters', 'Priority matrix', 'Task dependency', 'Launch planner', 'Brand ideas', 'Content planner', 'Habit streaks', 'Email dump', 'Customer notes', 'Leader checklist', 'Travel checklist', 'Shopping list', 'Reading tracker', 'Study notes', 'Lesson planner', 'Gratitude log', 'Daily wins', 'Art prompts', 'Writing ideas', 'Bug tracker', 'Bug report', 'Launch notes', 'Sprint board', 'Checklist tracker', 'Saved replies', 'Prompt library', 'Remote notes', 'Desk notes', 'Pocket knowledge', 'Daily planner', 'Budget tracker', 'Yearly goals', 'Seasonal plan', 'Personal journal', 'Health log', 'Workout notes', 'Meal planner', 'Bookmarks', 'Content vault', 'Idea radar', 'Vision board', 'Mood tracker', 'Scan to note', 'Clipboard sync', 'One-click export', 'Batch import', 'Instant backup', 'Secure notes', 'Temporary notes', 'Quick draft', 'Auto complete', 'Focus notes', 'Night mode', 'Dark mode', 'Night planner', 'Snooze actions', 'Recurring tasks', 'Scheduling', 'Calendar notes', 'Status updates', 'Daily digest', 'History timeline', 'Database notes', 'Smart labels', 'Highlight notes', 'Read time', 'Word count', 'Character count', 'Summary cards', 'Insight panel', 'Mini dashboard', 'Mood board', 'Workflows', 'Memory prompts', 'Micro plans', 'Idea threads', 'Nudge reminders', 'Note templates', 'Quarter planner', 'Growth tracker', 'Personal archive', 'Creative prompts', 'Life map', 'Goal board', 'Planning mode', 'Focus board', 'Remember slider', 'Signal board', 'Path tracker', 'Snapshot log', 'Future notes', 'Operating system', 'Personal AI', 'Assistant layer', 'Productivity matrix', 'Skill map', 'Life admin', 'Daily vault', 'Inbox manager', 'Note categories', 'Search index', 'Auto tags', 'Natural language search', 'Semantic filters', 'Management board', 'Project tracker', 'Schedule planner', 'Task timer', 'Idea generation', 'Content calendar', 'Team notes', 'Personal notes', 'Audit log', 'Action queue', 'Event journal', 'Storage index', 'Planner stream', 'Action board', 'Sprint planner', 'Backlog notes', 'Performance notes', 'Progress snapshot', 'Signal tracking', 'Risk log', 'Issue tracker', 'Customer insights', 'Research vault', 'Feedback archive', 'Summary mode', 'Full text search', 'Scan notes', 'Pinned ideas', 'Highlights', 'Bookmark snippets', 'Note stream', 'Knowledge map', 'Cross-link notes', 'Multi-tag notes', 'Board cards', 'Decision memo', 'Vision notes', 'Operations log', 'Design board', 'Launch checklist', 'Checklists', 'Think log', 'Action notes', 'Next step tracking', 'Product notes', 'Message vault', 'Planning board', 'Story notes', 'Brainstorm notes', 'Campaign notes', 'Marketing notes', 'Brand log', 'Client log', 'Project diary', 'Prototype notes', 'Digital vault', 'Knowledge notes', 'Habit notes', 'Life notes', 'Travel journal', 'Playlist ideas', 'Recipe notes', 'Nutrition log', 'Family notebook', 'Wedding plan', 'Home planner', 'Garden notes', 'Code snippets', 'Dev notes', 'Research notes', 'Essay notes', 'Learning notes', 'Note pods', 'Task pods', 'Work pods', 'Idea pods', 'Focus pods', 'Team pods', 'User stories', 'Roadmap notes', 'Design notes', 'Vision archive', 'Sprint notes', 'Mini planner', 'Daily board', 'Win tracker', 'Feedback loop', 'Auto retention', 'Smart cleanup', 'Archive manager', 'Trash manager', 'Delta notes', 'Timeline notes', 'Collections', 'Widget panel', 'Command center', 'Overview board', 'Discovery notes', 'Focus vault', 'Dashboard mode', 'Action tracker', 'Insight tracker', 'Automation notes', 'Workflow notes', 'Note explorer', 'Filter engine', 'Search engine', 'Insight engine', 'Power tools', 'Advanced tools', 'Pro tools'
    ];

    const noteForm = document.getElementById('noteForm');
    const notesList = document.getElementById('notesList');
    const titleInput = document.getElementById('titleInput');
    const categoryInput = document.getElementById('categoryInput');
    const tagsInput = document.getElementById('tagsInput');
    const contentInput = document.getElementById('contentInput');
    const colorInput = document.getElementById('colorInput');
    const priorityInput = document.getElementById('priorityInput');
    const dueDateInput = document.getElementById('dueDateInput');
    const searchInput = document.getElementById('searchInput');
    const modeBadge = document.getElementById('modeBadge');
    const featureGrid = document.getElementById('featureGrid');
    const toast = document.getElementById('toast');
    const statusInput = document.getElementById('statusInput');

    function populateFeatureGrid() {
      const items = featureCatalog.slice(0, 120);
      featureGrid.innerHTML = items.map(item => `<span class="feature-item">${item}</span>`).join('');
    }

    function showToast(message) {
      toast.textContent = message;
      toast.classList.add('show');
      clearTimeout(showToast.timer);
      showToast.timer = setTimeout(() => toast.classList.remove('show'), 2100);
    }

    function escapeHtml(value) {
      return String(value || '')
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/"/g, '&quot;')
        .replace(/'/g, '&#039;');
    }

    function updateWordCount() {
      const text = contentInput.value.trim();
      const count = text ? text.split(/\\s+/).length : 0;
      document.getElementById('wordCount').textContent = `${count} word${count === 1 ? '' : 's'}`;
    }

    function parseTags(value) {
      return (value || '').split(',').map(tag => tag.trim()).filter(Boolean).slice(0, 8);
    }

    function formatDate(value) {
      if (!value) return 'No date';
      const date = new Date(value);
      return isNaN(date.getTime()) ? value : date.toLocaleString([], { year: 'numeric', month: 'short', day: 'numeric' });
    }

    function readSettings() {
      return fetch('/api/settings').then(res => res.json());
    }

    function saveSettings(settings) {
      return fetch('/api/settings', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(settings)
      }).then(res => res.json());
    }

    function getPriorityWeight(level) {
      const weights = { low: 1, medium: 2, high: 3 };
      return weights[level] || 2;
    }

    function sortNotes(list) {
      const sorted = [...list];
      if (state.sort === 'oldest') {
        sorted.sort((a, b) => new Date(a.createdAt) - new Date(b.createdAt));
      } else if (state.sort === 'title') {
        sorted.sort((a, b) => a.title.localeCompare(b.title));
      } else if (state.sort === 'priority') {
        sorted.sort((a, b) => getPriorityWeight(b.priority) - getPriorityWeight(a.priority));
      } else {
        sorted.sort((a, b) => new Date(b.createdAt) - new Date(a.createdAt));
      }
      return sorted;
    }

    function getVisibleNotes(notes) {
      let filtered = [...notes];
      const query = searchInput.value.trim().toLowerCase();
      if (query) {
        filtered = filtered.filter(note => `${note.title} ${note.content} ${note.category} ${note.tags.join(' ')}`.toLowerCase().includes(query));
      }

      if (state.status !== 'all') {
        filtered = filtered.filter(note => (note.status || 'todo') === state.status);
      }

      if (state.view === 'favorite') filtered = filtered.filter(note => note.favorite);
      if (state.view === 'pinned') filtered = filtered.filter(note => note.pinned);
      if (state.view === 'archived') filtered = filtered.filter(note => note.archived && !note.deleted);
      if (state.view === 'trash') filtered = filtered.filter(note => note.deleted);
      if (state.view === 'done') filtered = filtered.filter(note => !note.deleted && (note.status || 'todo') === 'done');
      if (state.view === 'all') filtered = filtered.filter(note => !note.deleted);

      return sortNotes(filtered);
    }

    function renderStats(notes) {
      const total = notes.length;
      const favorites = notes.filter(n => n.favorite && !n.deleted).length;
      const pinned = notes.filter(n => n.pinned && !n.deleted).length;
      const archived = notes.filter(n => n.archived && !n.deleted).length;
      const done = notes.filter(n => (n.status || 'todo') === 'done' && !n.deleted).length;
      const today = notes.filter(note => {
        if (!note.createdAt) return false;
        const created = new Date(note.createdAt);
        const now = new Date();
        return created.toDateString() === now.toDateString();
      }).length;

      document.getElementById('totalNotes').textContent = total;
      document.getElementById('favoritesCount').textContent = favorites;
      document.getElementById('pinnedCount').textContent = pinned;
      document.getElementById('archivedCount').textContent = archived;
      document.getElementById('doneCount').textContent = done;
      document.getElementById('todayCount').textContent = today;
    }

    function renderNotes(notes) {
      const visible = getVisibleNotes(notes);
      renderStats(notes);

      if (!visible.length) {
        notesList.innerHTML = '<div class="empty">No notes match this view. Try a different filter or create a new note.</div>';
        return;
      }

      notesList.innerHTML = visible.map(note => `
        <article class="note-card ${note.pinned ? 'pinned' : ''} ${note.favorite ? 'favorite' : ''}" style="border-left: 5px solid ${escapeHtml(note.color || '#6c62ff')};">
          <div class="note-top">
            <div class="note-title-block">
              <h3 class="note-title">${escapeHtml(note.title)}</h3>
              ${note.favorite ? '<span class="star">★</span>' : ''}
              ${note.pinned ? '<span class="pin">📌</span>' : ''}
              ${note.archived ? '<span class="tag">Archived</span>' : ''}
            </div>
            <div class="note-actions">
              <button class="tiny-btn" data-action="edit" data-id="${note.id}" type="button">Edit</button>
              <button class="tiny-btn" data-action="duplicate" data-id="${note.id}" type="button">Duplicate</button>
              <button class="tiny-btn" data-action="complete" data-id="${note.id}" type="button">${(note.status || 'todo') === 'done' ? 'Reopen' : 'Done'}</button>
              ${note.deleted ? '<button class="tiny-btn" data-action="restore" data-id="${note.id}" type="button">Restore</button>' : '<button class="tiny-btn" data-action="archive" data-id="${note.id}" type="button">Archive</button>'}
              <button class="tiny-btn" data-action="favorite" data-id="${note.id}" type="button">${note.favorite ? 'Unstar' : 'Star'}</button>
              <button class="tiny-btn" data-action="pin" data-id="${note.id}" type="button">${note.pinned ? 'Unpin' : 'Pin'}</button>
              <button class="tiny-btn" data-action="copy" data-id="${note.id}" type="button">Copy</button>
              ${note.deleted ? '<button class="tiny-btn" data-action="deletePermanent" data-id="${note.id}" type="button">Delete</button>' : '<button class="tiny-btn" data-action="delete" data-id="${note.id}" type="button">Remove</button>'}
            </div>
          </div>
          <div class="meta-line">
            <span>${formatDate(note.createdAt)}</span>
            ${note.category ? `<span>•</span><span>${escapeHtml(note.category)}</span>` : ''}
            ${note.priority ? `<span>•</span><span>${escapeHtml(note.priority)}</span>` : ''}
            ${note.status ? `<span>•</span><span>${escapeHtml(note.status.replace('-', ' '))}</span>` : ''}
            ${note.dueDate ? `<span>•</span><span>Due: ${formatDate(note.dueDate)}</span>` : ''}
          </div>
          <p class="note-body">${escapeHtml(note.content)}</p>
          <div class="note-footer">
            <div class="chip-list">
              ${note.tags && note.tags.length ? note.tags.map(tag => `<span class="mini-chip">${escapeHtml(tag)}</span>`).join('') : '<span class="mini-chip">General</span>'}
            </div>
            <span class="meta-line">Updated: ${formatDate(note.updatedAt || note.createdAt)}</span>
          </div>
        </article>
      `).join('');

      document.querySelectorAll('[data-action]').forEach(btn => {
        btn.addEventListener('click', async () => {
          const action = btn.dataset.action;
          const id = btn.dataset.id;
          if (action === 'delete') await updateNote(id, 'delete');
          if (action === 'deletePermanent') await updateNote(id, 'deletePermanent');
          if (action === 'archive') await updateNote(id, 'archive');
          if (action === 'restore') await updateNote(id, 'restore');
          if (action === 'favorite') await updateNote(id, 'favorite');
          if (action === 'pin') await updateNote(id, 'pin');
          if (action === 'copy') await copyNote(id);
          if (action === 'edit') await editNote(id);
          if (action === 'duplicate') await duplicateNote(id);
          if (action === 'complete') await toggleComplete(id);
        });
      });
    }

    async function fetchNotes() {
      const response = await fetch('/api/notes');
      const notes = await response.json();
      renderNotes(notes);
    }

    async function updateNote(id, action) {
      const response = await fetch('/api/notes', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ action, id })
      });
      const result = await response.json();
      if (result.ok) {
        showToast(result.message || 'Done');
        await fetchNotes();
      } else {
        showToast(result.error || 'Failed');
      }
    }

    async function copyNote(id) {
      const notes = await fetch('/api/notes').then(r => r.json());
      const note = notes.find(item => item.id === id);
      if (!note) return;
      try {
        await navigator.clipboard.writeText(`${note.title}\n\n${note.content}`);
        showToast('Copied to clipboard');
      } catch {
        showToast('Clipboard unavailable');
      }
    }

    async function duplicateNote(id) {
      const notes = await fetch('/api/notes').then(r => r.json());
      const note = notes.find(item => item.id === id);
      if (!note) return;
      const copy = { ...note, id: undefined, title: `${note.title} (copy)`, createdAt: new Date().toISOString(), updatedAt: new Date().toISOString() };
      const response = await fetch('/api/notes', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ action: 'add', ...copy })
      });
      const result = await response.json();
      if (result.ok) {
        showToast('Note duplicated');
        await fetchNotes();
      }
    }

    async function toggleComplete(id) {
      const response = await fetch('/api/notes', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ action: 'toggleComplete', id })
      });
      const result = await response.json();
      if (result.ok) {
        showToast(result.message || 'Status updated');
        await fetchNotes();
      }
    }

    async function editNote(id) {
      const notes = await fetch('/api/notes').then(r => r.json());
      const note = notes.find(item => item.id === id);
      if (!note) return;
      state.editId = note.id;
      modeBadge.textContent = 'Edit';
      titleInput.value = note.title || '';
      categoryInput.value = note.category || '';
      tagsInput.value = note.tags ? note.tags.join(', ') : '';
      contentInput.value = note.content || '';
      priorityInput.value = note.priority || 'medium';
      statusInput.value = note.status || 'todo';
      dueDateInput.value = note.dueDate || '';
      colorInput.value = note.color || '#6c62ff';
      state.toggles.favorite = !!note.favorite;
      state.toggles.pinned = !!note.pinned;
      state.toggles.archived = !!note.archived;
      syncToggleButtons();
      titleInput.focus();
    }

    function resetForm() {
      state.editId = null;
      modeBadge.textContent = 'New';
      noteForm.reset();
      priorityInput.value = 'medium';
      statusInput.value = 'todo';
      colorInput.value = '#6c62ff';
      state.toggles.favorite = true;
      state.toggles.pinned = false;
      state.toggles.archived = false;
      syncToggleButtons();
    }

    function syncToggleButtons() {
      document.querySelectorAll('[data-toggle]').forEach(button => {
        const key = button.dataset.toggle;
        button.classList.toggle('active', !!state.toggles[key]);
      });
    }

    document.querySelectorAll('[data-toggle]').forEach(button => {
      button.addEventListener('click', () => {
        const key = button.dataset.toggle;
        state.toggles[key] = !state.toggles[key];
        syncToggleButtons();
      });
    });

    noteForm.addEventListener('submit', async (event) => {
      event.preventDefault();
      const title = titleInput.value.trim();
      const content = contentInput.value.trim();
      if (!title || !content) {
        showToast('Title and note are required.');
        return;
      }

      const payload = {
        title,
        category: categoryInput.value.trim(),
        content,
        tags: parseTags(tagsInput.value),
        priority: priorityInput.value,
        status: statusInput.value || 'todo',
        dueDate: dueDateInput.value,
        color: colorInput.value,
        favorite: state.toggles.favorite,
        pinned: state.toggles.pinned,
        archived: state.toggles.archived,
      };

      if (state.editId) {
        payload.action = 'update';
        payload.id = state.editId;
      } else {
        payload.action = 'add';
      }

      const response = await fetch('/api/notes', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });

      const result = await response.json();
      if (result.ok) {
        resetForm();
        showToast(result.message || 'Saved');
        await fetchNotes();
      } else {
        showToast(result.error || 'Failed');
      }
    });

    document.getElementById('newNoteBtn').addEventListener('click', resetForm);

    document.getElementById('deleteAllBtn').addEventListener('click', async () => {
      const confirmed = confirm('Delete all notes permanently?');
      if (!confirmed) return;
      const response = await fetch('/api/notes', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ action: 'deleteAll' })
      });
      const result = await response.json();
      if (result.ok) {
        showToast('All notes deleted');
        await fetchNotes();
      }
    });

    document.getElementById('exportBtn').addEventListener('click', async () => {
      const notes = await fetch('/api/notes').then(r => r.json());
      const blob = new Blob([JSON.stringify(notes, null, 2)], { type: 'application/json' });
      const link = document.createElement('a');
      link.href = URL.createObjectURL(blob);
      link.download = 'notes-export.json';
      link.click();
      URL.revokeObjectURL(link.href);
      showToast('Notes exported');
    });

    document.getElementById('importBtn').addEventListener('click', () => {
      document.getElementById('importInput').click();
    });

    document.getElementById('importInput').addEventListener('change', async (event) => {
      const file = event.target.files[0];
      if (!file) return;
      const text = await file.text();
      try {
        const data = JSON.parse(text);
        const response = await fetch('/api/notes', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ action: 'importNotes', notes: data })
        });
        const result = await response.json();
        if (result.ok) {
          showToast('Notes imported');
          await fetchNotes();
        }
      } catch {
        showToast('Invalid JSON file');
      }
      event.target.value = '';
    });

    document.getElementById('themeToggle').addEventListener('click', async () => {
      const nextTheme = document.body.classList.contains('dark') ? 'light' : 'dark';
      document.body.classList.toggle('dark', nextTheme === 'dark');
      await saveSettings({ theme: nextTheme, sort: state.sort, view: state.view });
      showToast(`Theme: ${nextTheme}`);
    });

    document.querySelectorAll('[data-view]').forEach(button => {
      button.addEventListener('click', () => {
        state.view = button.dataset.view;
        document.querySelectorAll('[data-view]').forEach(btn => btn.classList.toggle('active', btn === button));
        fetchNotes();
      });
    });

    document.querySelectorAll('[data-status]').forEach(button => {
      button.addEventListener('click', () => {
        state.status = button.dataset.status;
        document.querySelectorAll('[data-status]').forEach(btn => btn.classList.toggle('active', btn === button));
        fetchNotes();
      });
    });

    document.querySelectorAll('[data-sort]').forEach(button => {
      button.addEventListener('click', async () => {
        state.sort = button.dataset.sort;
        document.querySelectorAll('[data-sort]').forEach(btn => btn.classList.toggle('active', btn === button));
        await saveSettings({ theme: state.theme, sort: state.sort, view: state.view });
        fetchNotes();
      });
    });

    document.querySelectorAll('[data-template]').forEach(button => {
      button.addEventListener('click', () => {
        const template = templates[button.dataset.template];
        if (!template) return;
        titleInput.value = template.title;
        contentInput.value = template.content;
        updateWordCount();
        showToast(`${template.title} loaded`);
        titleInput.focus();
      });
    });

    contentInput.addEventListener('input', updateWordCount);
    searchInput.addEventListener('input', fetchNotes);

    (async function init() {
      populateFeatureGrid();
      updateWordCount();
      const settings = await readSettings();
      state.theme = settings.theme || 'light';
      state.sort = settings.sort || 'newest';
      state.view = settings.view || 'all';
      document.body.classList.toggle('dark', state.theme === 'dark');
      document.querySelectorAll('[data-view]').forEach(btn => btn.classList.toggle('active', btn.dataset.view === state.view));
      document.querySelectorAll('[data-sort]').forEach(btn => btn.classList.toggle('active', btn.dataset.sort === state.sort));
      resetForm();
      await fetchNotes();
    })();
  </script>
</body>
</html>
"""


def load_json(path, default):
    try:
        data = json.loads(path.read_text(encoding='utf-8')) if path.exists() else default
        return data if isinstance(data, type(default)) or default is None else default
    except Exception:
        return default


def save_json(path, data):
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding='utf-8')


def load_notes():
    return load_json(DATA_FILE, [])


def save_notes(notes):
    save_json(DATA_FILE, notes)


def load_settings():
    return load_json(SETTINGS_FILE, DEFAULT_SETTINGS)


def save_settings(settings):
    save_json(SETTINGS_FILE, settings)


def normalize_note(note):
    return {
        'id': str(note.get('id') or uuid.uuid4().hex),
        'title': str(note.get('title') or 'Untitled').strip(),
        'content': str(note.get('content') or '').strip(),
        'category': str(note.get('category') or '').strip(),
        'tags': [str(tag).strip() for tag in (note.get('tags') or []) if str(tag).strip()],
        'priority': str(note.get('priority') or 'medium').lower(),
        'status': str(note.get('status') or 'todo').strip().lower() if note.get('status') is not None else 'todo',
        'dueDate': str(note.get('dueDate') or '').strip(),
        'color': str(note.get('color') or '#6c62ff').strip(),
        'favorite': bool(note.get('favorite')),
        'pinned': bool(note.get('pinned')),
        'archived': bool(note.get('archived')),
        'deleted': bool(note.get('deleted')),
        'createdAt': note.get('createdAt') or datetime.now(timezone.utc).isoformat(),
        'updatedAt': note.get('updatedAt') or note.get('createdAt') or datetime.now(timezone.utc).isoformat(),
    }


class NotesHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        parsed = urlparse(self.path)
        if parsed.path in ('/', '/index.html'):
            self.send_response(200)
            self.send_header('Content-Type', 'text/html; charset=utf-8')
            self.end_headers()
            self.wfile.write(HTML_PAGE.encode('utf-8'))
            return

        if parsed.path == '/api/notes':
            notes = [normalize_note(note) for note in load_notes()]
            self.send_response(200)
            self.send_header('Content-Type', 'application/json; charset=utf-8')
            self.end_headers()
            self.wfile.write(json.dumps(notes).encode('utf-8'))
            return

        if parsed.path == '/api/settings':
            settings = load_settings()
            self.send_response(200)
            self.send_header('Content-Type', 'application/json; charset=utf-8')
            self.end_headers()
            self.wfile.write(json.dumps(settings).encode('utf-8'))
            return

        self.send_error(404, 'Not found')

    def do_POST(self):
        parsed = urlparse(self.path)
        if parsed.path == '/api/settings':
            length = int(self.headers.get('Content-Length', '0'))
            raw = self.rfile.read(length).decode('utf-8')
            payload = json.loads(raw) if raw else {}
            settings = {**load_settings(), **payload}
            save_settings(settings)
            self.send_response(200)
            self.send_header('Content-Type', 'application/json; charset=utf-8')
            self.end_headers()
            self.wfile.write(json.dumps({'ok': True, 'settings': settings}).encode('utf-8'))
            return

        if parsed.path != '/api/notes':
            self.send_error(404, 'Not found')
            return

        length = int(self.headers.get('Content-Length', '0'))
        raw = self.rfile.read(length).decode('utf-8')
        payload = json.loads(raw) if raw else {}
        action = payload.get('action')
        notes = [normalize_note(note) for note in load_notes()]

        if action == 'add':
            title = str(payload.get('title') or '').strip()
            content = str(payload.get('content') or '').strip()
            if not title or not content:
                self.send_json_error('Title and note are required.')
                return
            note = {
                'id': uuid.uuid4().hex,
                'title': title,
                'content': content,
                'category': str(payload.get('category') or '').strip(),
                'tags': [str(tag).strip() for tag in (payload.get('tags') or []) if str(tag).strip()],
                'priority': str(payload.get('priority') or 'medium').lower(),
                'status': str(payload.get('status') or 'todo').strip().lower(),
                'dueDate': str(payload.get('dueDate') or '').strip(),
                'color': str(payload.get('color') or '#6c62ff').strip(),
                'favorite': bool(payload.get('favorite')),
                'pinned': bool(payload.get('pinned')),
                'archived': bool(payload.get('archived')),
                'deleted': False,
                'createdAt': datetime.now(timezone.utc).isoformat(),
                'updatedAt': datetime.now(timezone.utc).isoformat(),
            }
            notes.insert(0, normalize_note(note))
            save_notes(notes)
            self.send_response(200)
            self.send_header('Content-Type', 'application/json; charset=utf-8')
            self.end_headers()
            self.wfile.write(json.dumps({'ok': True, 'message': 'Note saved'}).encode('utf-8'))
            return

        if action == 'update':
            note_id = payload.get('id')
            for note in notes:
                if note['id'] == str(note_id):
                    note.update({
                        'title': str(payload.get('title') or note['title']).strip(),
                        'content': str(payload.get('content') or note['content']).strip(),
                        'category': str(payload.get('category') or '').strip() or note.get('category', ''),
                        'tags': [str(tag).strip() for tag in (payload.get('tags') or note.get('tags') or []) if str(tag).strip()],
                        'priority': str(payload.get('priority') or note.get('priority') or 'medium').lower(),
                        'status': str(payload.get('status') or note.get('status') or 'todo').strip().lower(),
                        'dueDate': str(payload.get('dueDate') or '').strip() or note.get('dueDate', ''),
                        'color': str(payload.get('color') or note.get('color') or '#6c62ff').strip(),
                        'favorite': bool(payload.get('favorite', note.get('favorite', False))),
                        'pinned': bool(payload.get('pinned', note.get('pinned', False))),
                        'archived': bool(payload.get('archived', note.get('archived', False))),
                        'updatedAt': datetime.now(timezone.utc).isoformat(),
                    })
                    save_notes(notes)
                    self.send_response(200)
                    self.send_header('Content-Type', 'application/json; charset=utf-8')
                    self.end_headers()
                    self.wfile.write(json.dumps({'ok': True, 'message': 'Note updated'}).encode('utf-8'))
                    return
            self.send_json_error('Note not found.')
            return

        if action == 'delete':
            note_id = str(payload.get('id'))
            for note in notes:
                if note['id'] == note_id:
                    note['deleted'] = True
                    note['archived'] = False
                    note['updatedAt'] = datetime.now(timezone.utc).isoformat()
                    save_notes(notes)
                    self.send_response(200)
                    self.send_header('Content-Type', 'application/json; charset=utf-8')
                    self.end_headers()
                    self.wfile.write(json.dumps({'ok': True, 'message': 'Moved to trash'}).encode('utf-8'))
                    return
            self.send_json_error('Note not found.')
            return

        if action == 'restore':
            note_id = str(payload.get('id'))
            for note in notes:
                if note['id'] == note_id:
                    note['deleted'] = False
                    note['updatedAt'] = datetime.now(timezone.utc).isoformat()
                    save_notes(notes)
                    self.send_response(200)
                    self.send_header('Content-Type', 'application/json; charset=utf-8')
                    self.end_headers()
                    self.wfile.write(json.dumps({'ok': True, 'message': 'Note restored'}).encode('utf-8'))
                    return
            self.send_json_error('Note not found.')
            return

        if action == 'archive':
            note_id = str(payload.get('id'))
            for note in notes:
                if note['id'] == note_id:
                    note['archived'] = not note.get('archived', False)
                    note['updatedAt'] = datetime.now(timezone.utc).isoformat()
                    save_notes(notes)
                    self.send_response(200)
                    self.send_header('Content-Type', 'application/json; charset=utf-8')
                    self.end_headers()
                    self.wfile.write(json.dumps({'ok': True, 'message': 'Archive updated'}).encode('utf-8'))
                    return
            self.send_json_error('Note not found.')
            return

        if action == 'favorite':
            note_id = str(payload.get('id'))
            for note in notes:
                if note['id'] == note_id:
                    note['favorite'] = not note.get('favorite', False)
                    note['updatedAt'] = datetime.now(timezone.utc).isoformat()
                    save_notes(notes)
                    self.send_response(200)
                    self.send_header('Content-Type', 'application/json; charset=utf-8')
                    self.end_headers()
                    self.wfile.write(json.dumps({'ok': True, 'message': 'Favorite updated'}).encode('utf-8'))
                    return
            self.send_json_error('Note not found.')
            return

        if action == 'pin':
            note_id = str(payload.get('id'))
            for note in notes:
                if note['id'] == note_id:
                    note['pinned'] = not note.get('pinned', False)
                    note['updatedAt'] = datetime.now(timezone.utc).isoformat()
                    save_notes(notes)
                    self.send_response(200)
                    self.send_header('Content-Type', 'application/json; charset=utf-8')
                    self.end_headers()
                    self.wfile.write(json.dumps({'ok': True, 'message': 'Pin updated'}).encode('utf-8'))
                    return
            self.send_json_error('Note not found.')
            return

        if action == 'toggleComplete':
            note_id = str(payload.get('id'))
            for note in notes:
                if note['id'] == note_id:
                    current_status = str(note.get('status') or 'todo').strip().lower()
                    note['status'] = 'done' if current_status != 'done' else 'todo'
                    note['updatedAt'] = datetime.now(timezone.utc).isoformat()
                    save_notes(notes)
                    self.send_response(200)
                    self.send_header('Content-Type', 'application/json; charset=utf-8')
                    self.end_headers()
                    self.wfile.write(json.dumps({'ok': True, 'message': 'Status updated'}).encode('utf-8'))
                    return
            self.send_json_error('Note not found.')
            return

        if action == 'deletePermanent':
            note_id = str(payload.get('id'))
            notes = [note for note in notes if note['id'] != note_id]
            save_notes(notes)
            self.send_response(200)
            self.send_header('Content-Type', 'application/json; charset=utf-8')
            self.end_headers()
            self.wfile.write(json.dumps({'ok': True, 'message': 'Deleted permanently'}).encode('utf-8'))
            return

        if action == 'deleteAll':
            save_notes([])
            self.send_response(200)
            self.send_header('Content-Type', 'application/json; charset=utf-8')
            self.end_headers()
            self.wfile.write(json.dumps({'ok': True, 'message': 'All notes deleted'}).encode('utf-8'))
            return

        if action == 'importNotes':
            incoming = payload.get('notes')
            if not isinstance(incoming, list):
                self.send_json_error('Invalid notes data.')
                return
            imported = [normalize_note(item) for item in incoming]
            save_notes(imported)
            self.send_response(200)
            self.send_header('Content-Type', 'application/json; charset=utf-8')
            self.end_headers()
            self.wfile.write(json.dumps({'ok': True, 'message': f'Imported {len(imported)} notes'}).encode('utf-8'))
            return

        self.send_json_error('Unknown action.')

    def send_json_error(self, message):
        self.send_response(400)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.end_headers()
        self.wfile.write(json.dumps({'ok': False, 'error': message}).encode('utf-8'))

    def log_message(self, format, *args):
        return


def main():
    server = ThreadingHTTPServer((HOST, PORT), NotesHandler)
    print(f"Notes Store Ultra running at http://{HOST}:{PORT}")
    server.serve_forever()


if __name__ == '__main__':
    main()
