<?php
require_once 'db.php';

// Get today's date
$today = date('Y-m-d');
$displayDate = date('l, F j, Y');
$currentTime = date('H:i');

// Fetch today's tasks
$tasks = [];
try {
    $stmt = $pdo->prepare("SELECT * FROM tasks WHERE task_date = ? ORDER BY priority_score ASC NULLS LAST, created_at ASC");
    $stmt->execute([$today]);
    $tasks = $stmt->fetchAll(PDO::FETCH_ASSOC);
} catch (Exception $e) {
    $dbError = $e->getMessage();
}

// Count stats
$totalTasks = count($tasks);
$completedTasks = count(array_filter($tasks, fn($t) => $t['status'] === 'completed'));
$pendingTasks = $totalTasks - $completedTasks;
?>
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>DayFlow — Daily Task Tracker</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link href="https://fonts.googleapis.com/css2?family=Playfair+Display:wght@400;700&family=DM+Sans:wght@300;400;500;600&family=DM+Mono:wght@400;500&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="/static/css/style.css">
</head>
<body>

<div class="bg-orbs">
    <div class="orb orb-1"></div>
    <div class="orb orb-2"></div>
    <div class="orb orb-3"></div>
</div>

<div class="container">

    <!-- Header -->
    <header class="header">
        <div class="header-left">
            <div class="logo">DayFlow</div>
            <div class="tagline">Your intelligent daily planner</div>
        </div>
        <div class="header-right">
            <div class="date-badge">
                <span class="date-icon">📅</span>
                <div>
                    <div class="date-main"><?= htmlspecialchars($displayDate) ?></div>
                    <div class="date-time" id="live-time"><?= $currentTime ?></div>
                </div>
            </div>
        </div>
    </header>

    <!-- Stats Bar -->
    <div class="stats-bar">
        <div class="stat-card">
            <span class="stat-num"><?= $totalTasks ?></span>
            <span class="stat-label">Total Tasks</span>
        </div>
        <div class="stat-card stat-pending">
            <span class="stat-num"><?= $pendingTasks ?></span>
            <span class="stat-label">Pending</span>
        </div>
        <div class="stat-card stat-done">
            <span class="stat-num"><?= $completedTasks ?></span>
            <span class="stat-label">Completed</span>
        </div>
        <div class="stat-card stat-progress">
            <span class="stat-num"><?= $totalTasks > 0 ? round(($completedTasks / $totalTasks) * 100) : 0 ?>%</span>
            <span class="stat-label">Progress</span>
        </div>
    </div>

    <?php if (isset($dbError)): ?>
    <div class="alert alert-error">
        ⚠️ Database connection error: <?= htmlspecialchars($dbError) ?>. Please check your PostgreSQL connection.
    </div>
    <?php endif; ?>

    <!-- Add Task Form -->
    <div class="card form-card">
        <div class="card-header">
            <h2>✦ What are your important tasks for today?</h2>
            <p>Fill in the details below — priority will be auto-calculated based on your deadline</p>
        </div>

        <form id="task-form" action="/api.php" method="POST">
            <input type="hidden" name="action" value="add_task">
            <input type="hidden" name="task_date" value="<?= $today ?>">

            <div class="form-grid">
                <!-- Column A: Task Description -->
                <div class="form-group col-a">
                    <label for="description">
                        Task Description <span class="required">*</span>
                        <span class="char-hint">max 300 chars</span>
                    </label>
                    <textarea
                        id="description"
                        name="description"
                        maxlength="300"
                        required
                        placeholder="Describe your task clearly..."
                        rows="3"
                    ></textarea>
                    <div class="char-counter"><span id="desc-count">0</span>/300</div>
                </div>

                <!-- Column B: Dependencies -->
                <div class="form-group col-b">
                    <label for="dependencies">
                        Dependencies
                        <span class="optional">optional</span>
                        <span class="char-hint">max 200 chars</span>
                    </label>
                    <textarea
                        id="dependencies"
                        name="dependencies"
                        maxlength="200"
                        placeholder="What does this task depend on? (e.g. waiting for feedback from John)"
                        rows="3"
                    ></textarea>
                    <div class="char-counter"><span id="dep-count">0</span>/200</div>
                </div>

                <!-- Column C: Deadline -->
                <div class="form-group col-c">
                    <label for="deadline_time">
                        Deadline Time <span class="required">*</span>
                    </label>
                    <input
                        type="time"
                        id="deadline_time"
                        name="deadline_time"
                        required
                    >
                    <div class="deadline-hint" id="time-until"></div>
                </div>

                <!-- Column D: Status -->
                <div class="form-group col-d">
                    <label for="status">Status</label>
                    <select id="status" name="status">
                        <option value="not_started">Not Started</option>
                        <option value="in_progress">In Progress</option>
                        <option value="blocked">Blocked</option>
                        <option value="completed">Completed</option>
                    </select>
                    <div class="status-notes-wrap">
                        <textarea
                            name="status_notes"
                            maxlength="300"
                            placeholder="Status notes... (optional)"
                            rows="2"
                        ></textarea>
                    </div>
                </div>
            </div>

            <div class="form-footer">
                <div class="priority-preview" id="priority-preview">
                    <span class="priority-label">Priority Score Preview:</span>
                    <span class="priority-value" id="priority-val">—</span>
                    <span class="priority-hint">Enter a deadline to see priority</span>
                </div>
                <button type="submit" class="btn-submit">
                    <span>Add Task</span>
                    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><line x1="12" y1="5" x2="12" y2="19"/><line x1="5" y1="12" x2="19" y2="12"/></svg>
                </button>
            </div>
        </form>
    </div>

    <!-- Task Table -->
    <div class="card table-card">
        <div class="card-header">
            <h2>📋 Today's Task Board</h2>
            <div class="filter-row">
                <button class="filter-btn active" data-filter="all">All</button>
                <button class="filter-btn" data-filter="not_started">Not Started</button>
                <button class="filter-btn" data-filter="in_progress">In Progress</button>
                <button class="filter-btn" data-filter="blocked">Blocked</button>
                <button class="filter-btn" data-filter="completed">Completed</button>
            </div>
        </div>

        <?php if (empty($tasks)): ?>
        <div class="empty-state">
            <div class="empty-icon">🌅</div>
            <div class="empty-title">No tasks yet for today</div>
            <div class="empty-sub">Add your first task above and start planning your day!</div>
        </div>
        <?php else: ?>
        <div class="table-wrapper">
            <table class="task-table">
                <thead>
                    <tr>
                        <th class="th-priority">Priority</th>
                        <th class="th-desc">Task Description</th>
                        <th class="th-dep">Dependencies</th>
                        <th class="th-deadline">Deadline</th>
                        <th class="th-status">Status</th>
                        <th class="th-actions">Actions</th>
                    </tr>
                </thead>
                <tbody id="task-tbody">
                    <?php foreach ($tasks as $task): ?>
                    <tr class="task-row" data-status="<?= htmlspecialchars($task['status']) ?>" data-id="<?= $task['id'] ?>">
                        <td class="td-priority">
                            <?php
                            $score = $task['priority_score'];
                            $badge = 'badge-low';
                            $label = 'Low';
                            if ($score !== null) {
                                if ($score <= 3) { $badge = 'badge-critical'; $label = 'P'.$score.' 🔥'; }
                                elseif ($score <= 6) { $badge = 'badge-high'; $label = 'P'.$score.' ⚡'; }
                                elseif ($score <= 9) { $badge = 'badge-medium'; $label = 'P'.$score.' 📌'; }
                                else { $badge = 'badge-low'; $label = 'P'.$score; }
                            }
                            ?>
                            <span class="priority-badge <?= $badge ?>"><?= $label ?></span>
                        </td>
                        <td class="td-desc">
                            <div class="task-desc"><?= htmlspecialchars($task['description']) ?></div>
                            <div class="task-meta">Added <?= date('g:i A', strtotime($task['created_at'])) ?></div>
                        </td>
                        <td class="td-dep">
                            <?php if ($task['dependencies']): ?>
                                <span class="dep-text"><?= htmlspecialchars($task['dependencies']) ?></span>
                            <?php else: ?>
                                <span class="no-dep">—</span>
                            <?php endif; ?>
                        </td>
                        <td class="td-deadline">
                            <div class="deadline-display">
                                <?= date('g:i A', strtotime($task['deadline_time'])) ?>
                            </div>
                            <div class="time-remaining" data-deadline="<?= $task['deadline_time'] ?>"></div>
                        </td>
                        <td class="td-status">
                            <select class="status-select" data-id="<?= $task['id'] ?>">
                                <option value="not_started" <?= $task['status']==='not_started' ? 'selected' : '' ?>>Not Started</option>
                                <option value="in_progress" <?= $task['status']==='in_progress' ? 'selected' : '' ?>>In Progress</option>
                                <option value="blocked" <?= $task['status']==='blocked' ? 'selected' : '' ?>>Blocked</option>
                                <option value="completed" <?= $task['status']==='completed' ? 'selected' : '' ?>>Completed</option>
                            </select>
                            <?php if ($task['status_notes']): ?>
                            <div class="status-notes"><?= htmlspecialchars($task['status_notes']) ?></div>
                            <?php endif; ?>
                        </td>
                        <td class="td-actions">
                            <button class="btn-delete" data-id="<?= $task['id'] ?>" title="Delete task">
                                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="3 6 5 6 21 6"/><path d="M19 6l-1 14H6L5 6"/><path d="M10 11v6M14 11v6"/><path d="M9 6V4h6v2"/></svg>
                            </button>
                        </td>
                    </tr>
                    <?php endforeach; ?>
                </tbody>
            </table>
        </div>
        <?php endif; ?>
    </div>

</div>

<div id="toast" class="toast"></div>

<script>
    const TODAY = '<?= $today ?>';
    const CURRENT_TIME = '<?= date('H:i') ?>';
</script>
<script src="/static/js/app.js"></script>
</body>
</html>