/**
 * DayFlow — app.js
 * Handles: live clock, char counters, priority preview,
 *          time-remaining display, status updates, delete, filters
 */

// ── Live Clock ────────────────────────────────────────────────
function updateClock() {
    const el = document.getElementById('live-time');
    if (!el) return;
    const now = new Date();
    const h = String(now.getHours()).padStart(2, '0');
    const m = String(now.getMinutes()).padStart(2, '0');
    const s = String(now.getSeconds()).padStart(2, '0');
    el.textContent = `${h}:${m}:${s}`;
}
setInterval(updateClock, 1000);
updateClock();

// ── Toast Notification ────────────────────────────────────────
function showToast(msg, type = 'success') {
    const toast = document.getElementById('toast');
    if (!toast) return;
    toast.textContent = msg;
    toast.className = `toast ${type} show`;
    setTimeout(() => { toast.className = 'toast'; }, 3500);
}

// ── Character Counters ────────────────────────────────────────
const descArea = document.getElementById('description');
const depArea  = document.getElementById('dependencies');
const descCount = document.getElementById('desc-count');
const depCount  = document.getElementById('dep-count');

if (descArea && descCount) {
    descArea.addEventListener('input', () => {
        descCount.textContent = descArea.value.length;
        descCount.style.color = descArea.value.length > 270 ? '#ff5566' : '';
    });
}

if (depArea && depCount) {
    depArea.addEventListener('input', () => {
        depCount.textContent = depArea.value.length;
        depCount.style.color = depArea.value.length > 180 ? '#ff5566' : '';
    });
}

// ── Priority Preview ──────────────────────────────────────────
const deadlineInput = document.getElementById('deadline_time');
const priorityVal   = document.getElementById('priority-val');
const priorityHint  = document.querySelector('.priority-hint');
const deadlineHint  = document.getElementById('time-until');

let previewTimeout;

function getUrgencyLabel(score) {
    if (score <= 2) return { text: '🔥 Critical — Do this first!', color: '#ff5566' };
    if (score <= 4) return { text: '⚡ High Priority', color: '#ff8040' };
    if (score <= 6) return { text: '📌 Medium Priority', color: '#f0c060' };
    return { text: '✓ Low Priority', color: '#60c0a0' };
}

function getTimeUntil(timeStr) {
    const now = new Date();
    const [h, m] = timeStr.split(':').map(Number);
    const deadline = new Date();
    deadline.setHours(h, m, 0, 0);

    const diffMs = deadline - now;
    if (diffMs < 0) return { text: '⚠ Deadline passed', cls: 'overdue' };

    const diffMins = Math.floor(diffMs / 60000);
    const hours = Math.floor(diffMins / 60);
    const mins  = diffMins % 60;

    let cls = 'ok';
    if (diffMins <= 60)  cls = 'urgent';
    else if (diffMins <= 180) cls = 'soon';

    const text = hours > 0
        ? `${hours}h ${mins}m remaining`
        : `${mins}m remaining`;

    return { text, cls };
}

if (deadlineInput) {
    deadlineInput.addEventListener('change', () => {
        const val = deadlineInput.value;
        if (!val) return;

        // Show time until
        if (deadlineHint) {
            const { text, cls } = getTimeUntil(val);
            deadlineHint.textContent = text;
            deadlineHint.className = `deadline-hint ${cls}`;
        }

        // Debounce priority preview API call
        clearTimeout(previewTimeout);
        previewTimeout = setTimeout(async () => {
            try {
                const res = await fetch(`/api.php?action=preview_priority&deadline=${encodeURIComponent(val)}&date=${TODAY}`);
                const data = await res.json();
                if (data.success && data.score !== null) {
                    if (priorityVal) priorityVal.textContent = `P${data.score}`;
                    if (priorityHint) {
                        const { text, color } = getUrgencyLabel(data.score);
                        priorityHint.textContent = text;
                        priorityHint.style.color = color;
                    }
                }
            } catch (e) {
                // Silently fail — priority preview is non-critical
            }
        }, 400);
    });
}

// ── Time Remaining on Table Rows ─────────────────────────────
function updateTimeRemaining() {
    document.querySelectorAll('.time-remaining[data-deadline]').forEach(el => {
        const timeStr = el.dataset.deadline.substring(0, 5); // HH:MM
        const { text, cls } = getTimeUntil(timeStr);
        el.textContent = text;
        el.className = `time-remaining ${cls}`;
    });
}
updateTimeRemaining();
setInterval(updateTimeRemaining, 60000);

// ── Task Form Submission ──────────────────────────────────────
const taskForm = document.getElementById('task-form');
if (taskForm) {
    taskForm.addEventListener('submit', async (e) => {
        e.preventDefault();

        const desc = document.getElementById('description').value.trim();
        const deadline = document.getElementById('deadline_time').value;

        if (!desc) { showToast('Task description is required.', 'error'); return; }
        if (!deadline) { showToast('Deadline time is required.', 'error'); return; }

        const btn = taskForm.querySelector('.btn-submit');
        btn.disabled = true;
        btn.querySelector('span').textContent = 'Adding...';

        try {
            const formData = new FormData(taskForm);
            const res = await fetch('/api.php', { method: 'POST', body: formData });
            const data = await res.json();

            if (data.success) {
                showToast('✓ Task added successfully!', 'success');
                setTimeout(() => window.location.reload(), 800);
            } else {
                const errs = data.errors ? data.errors.join(' ') : (data.error || 'Failed to add task.');
                showToast(errs, 'error');
                btn.disabled = false;
                btn.querySelector('span').textContent = 'Add Task';
            }
        } catch (err) {
            showToast('Network error. Please try again.', 'error');
            btn.disabled = false;
            btn.querySelector('span').textContent = 'Add Task';
        }
    });
}

// ── Status Update ─────────────────────────────────────────────
document.querySelectorAll('.status-select').forEach(select => {
    select.addEventListener('change', async () => {
        const id     = select.dataset.id;
        const status = select.value;
        const row    = select.closest('.task-row');

        try {
            const fd = new FormData();
            fd.append('action', 'update_status');
            fd.append('id', id);
            fd.append('status', status);

            const res = await fetch('/api.php', { method: 'POST', body: fd });
            const data = await res.json();

            if (data.success) {
                if (row) row.dataset.status = status;
                showToast('Status updated', 'success');
                // Re-apply active filter
                const activeFilter = document.querySelector('.filter-btn.active');
                if (activeFilter) applyFilter(activeFilter.dataset.filter);
            } else {
                showToast('Failed to update status', 'error');
            }
        } catch (err) {
            showToast('Network error', 'error');
        }
    });
});

// ── Delete Task ───────────────────────────────────────────────
document.querySelectorAll('.btn-delete').forEach(btn => {
    btn.addEventListener('click', async () => {
        if (!confirm('Delete this task?')) return;

        const id = btn.dataset.id;

        try {
            const fd = new FormData();
            fd.append('action', 'delete_task');
            fd.append('id', id);

            const res = await fetch('/api.php', { method: 'POST', body: fd });
            const data = await res.json();

            if (data.success) {
                const row = btn.closest('.task-row');
                if (row) {
                    row.style.opacity = '0';
                    row.style.transform = 'translateX(20px)';
                    row.style.transition = 'opacity 0.3s, transform 0.3s';
                    setTimeout(() => { row.remove(); updateStats(); }, 300);
                }
                showToast('Task deleted', 'success');
            } else {
                showToast('Failed to delete task', 'error');
            }
        } catch (err) {
            showToast('Network error', 'error');
        }
    });
});

// ── Filter Buttons ────────────────────────────────────────────
function applyFilter(filter) {
    document.querySelectorAll('.task-row').forEach(row => {
        if (filter === 'all' || row.dataset.status === filter) {
            row.classList.remove('hidden');
        } else {
            row.classList.add('hidden');
        }
    });
}

document.querySelectorAll('.filter-btn').forEach(btn => {
    btn.addEventListener('click', () => {
        document.querySelectorAll('.filter-btn').forEach(b => b.classList.remove('active'));
        btn.classList.add('active');
        applyFilter(btn.dataset.filter);
    });
});

// ── Update Stats After Delete ─────────────────────────────────
function updateStats() {
    const rows    = document.querySelectorAll('.task-row');
    const total   = rows.length;
    const done    = [...rows].filter(r => r.dataset.status === 'completed').length;
    const pending = total - done;
    const pct     = total > 0 ? Math.round((done / total) * 100) : 0;

    const statNums = document.querySelectorAll('.stat-num');
    if (statNums[0]) statNums[0].textContent = total;
    if (statNums[1]) statNums[1].textContent = pending;
    if (statNums[2]) statNums[2].textContent = done;
    if (statNums[3]) statNums[3].textContent = pct + '%';
}

// ── Animate rows on load ──────────────────────────────────────
document.querySelectorAll('.task-row').forEach((row, i) => {
    row.style.opacity = '0';
    row.style.transform = 'translateY(10px)';
    row.style.transition = 'opacity 0.3s, transform 0.3s';
    setTimeout(() => {
        row.style.opacity = '1';
        row.style.transform = 'translateY(0)';
    }, 60 * i + 100);
});