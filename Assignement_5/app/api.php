<?php
/**
 * API Handler — handles all AJAX and form POST requests
 */

header('Content-Type: application/json');
require_once 'db.php';

$action = $_POST['action'] ?? $_GET['action'] ?? '';

/**
 * Calculate priority score (1 = most urgent, higher = less urgent)
 * Logic: Tasks closer to their deadline get a lower (higher priority) score.
 * We factor in time remaining AND compare against other tasks today.
 */
function calculatePriorityScore(PDO $pdo, string $deadlineTime, string $taskDate, ?int $excludeId = null): int {
    $now = new DateTime();
    $deadline = new DateTime($taskDate . ' ' . $deadlineTime);

    // Minutes until deadline (can be negative if overdue)
    $diffMinutes = ($deadline->getTimestamp() - $now->getTimestamp()) / 60;

    // Base score: bucket by urgency
    if ($diffMinutes < 0)       $baseScore = 1;   // Overdue → critical
    elseif ($diffMinutes <= 60) $baseScore = 2;   // < 1 hour
    elseif ($diffMinutes <= 180) $baseScore = 4;  // 1–3 hours
    elseif ($diffMinutes <= 360) $baseScore = 6;  // 3–6 hours
    elseif ($diffMinutes <= 480) $baseScore = 8;  // 6–8 hours
    else                         $baseScore = 10; // > 8 hours

    // Re-rank all tasks for today including this one
    $query = "SELECT id, deadline_time FROM tasks WHERE task_date = ?";
    $params = [$taskDate];
    if ($excludeId) {
        $query .= " AND id != ?";
        $params[] = $excludeId;
    }
    $stmt = $pdo->prepare($query);
    $stmt->execute($params);
    $existing = $stmt->fetchAll();

    // Build ranking: collect all deadlines + new one, sort, assign rank
    $allDeadlines = [];
    foreach ($existing as $row) {
        $allDeadlines[] = $row['deadline_time'];
    }
    $allDeadlines[] = $deadlineTime;
    sort($allDeadlines);

    $rank = array_search($deadlineTime, $allDeadlines) + 1;

    // Final score blends base urgency with rank among today's tasks
    return max(1, min(10, (int) round(($baseScore + $rank) / 2)));
}

try {
    switch ($action) {

        // ── ADD TASK ──────────────────────────────────────────────
        case 'add_task':
            $description   = trim($_POST['description'] ?? '');
            $dependencies  = trim($_POST['dependencies'] ?? '');
            $deadlineTime  = $_POST['deadline_time'] ?? '';
            $status        = $_POST['status'] ?? 'not_started';
            $statusNotes   = trim($_POST['status_notes'] ?? '');
            $taskDate      = $_POST['task_date'] ?? date('Y-m-d');

            // Validation
            $errors = [];
            if (empty($description))  $errors[] = 'Task description is required.';
            if (strlen($description) > 300) $errors[] = 'Description must be 300 characters or less.';
            if (strlen($dependencies) > 200) $errors[] = 'Dependencies must be 200 characters or less.';
            if (empty($deadlineTime)) $errors[] = 'Deadline time is required.';
            if (!in_array($status, ['not_started','in_progress','blocked','completed']))
                $errors[] = 'Invalid status value.';

            if (!empty($errors)) {
                echo json_encode(['success' => false, 'errors' => $errors]);
                exit;
            }

            $priorityScore = calculatePriorityScore($pdo, $deadlineTime, $taskDate);

            $stmt = $pdo->prepare("
                INSERT INTO tasks (task_date, description, dependencies, deadline_time, status, status_notes, priority_score)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                RETURNING id
            ");
            $stmt->execute([
                $taskDate,
                $description,
                $dependencies ?: null,
                $deadlineTime,
                $status,
                $statusNotes ?: null,
                $priorityScore
            ]);
            $newId = $stmt->fetchColumn();

            // Re-calculate priorities for all tasks today
            recalcAllPriorities($pdo, $taskDate);

            echo json_encode(['success' => true, 'id' => $newId, 'redirect' => '/']);
            break;

        // ── UPDATE STATUS ─────────────────────────────────────────
        case 'update_status':
            $id     = (int)($_POST['id'] ?? 0);
            $status = $_POST['status'] ?? '';

            if (!$id || !in_array($status, ['not_started','in_progress','blocked','completed'])) {
                echo json_encode(['success' => false, 'error' => 'Invalid input.']);
                exit;
            }

            $stmt = $pdo->prepare("UPDATE tasks SET status = ?, updated_at = NOW() WHERE id = ?");
            $stmt->execute([$status, $id]);

            echo json_encode(['success' => true]);
            break;

        // ── DELETE TASK ───────────────────────────────────────────
        case 'delete_task':
            $id = (int)($_POST['id'] ?? 0);
            if (!$id) {
                echo json_encode(['success' => false, 'error' => 'Invalid task ID.']);
                exit;
            }

            // Get date before deleting for recalc
            $stmt = $pdo->prepare("SELECT task_date FROM tasks WHERE id = ?");
            $stmt->execute([$id]);
            $row = $stmt->fetch();
            $taskDate = $row ? $row['task_date'] : date('Y-m-d');

            $stmt = $pdo->prepare("DELETE FROM tasks WHERE id = ?");
            $stmt->execute([$id]);

            recalcAllPriorities($pdo, $taskDate);

            echo json_encode(['success' => true]);
            break;

        // ── PREVIEW PRIORITY ──────────────────────────────────────
        case 'preview_priority':
            $deadlineTime = $_GET['deadline'] ?? '';
            $taskDate     = $_GET['date'] ?? date('Y-m-d');

            if (empty($deadlineTime)) {
                echo json_encode(['success' => false, 'score' => null]);
                exit;
            }

            $score = calculatePriorityScore($pdo, $deadlineTime, $taskDate);
            echo json_encode(['success' => true, 'score' => $score]);
            break;

        default:
            echo json_encode(['success' => false, 'error' => 'Unknown action.']);
    }

} catch (Exception $e) {
    echo json_encode(['success' => false, 'error' => 'Server error: ' . $e->getMessage()]);
}

/**
 * Recalculate priority scores for ALL tasks on a given date.
 * Called after any add/delete to keep rankings consistent.
 */
function recalcAllPriorities(PDO $pdo, string $taskDate): void {
    $stmt = $pdo->prepare("SELECT id, deadline_time FROM tasks WHERE task_date = ? ORDER BY deadline_time ASC");
    $stmt->execute([$taskDate]);
    $tasks = $stmt->fetchAll();

    foreach ($tasks as $rank => $task) {
        $now      = new DateTime();
        $deadline = new DateTime($taskDate . ' ' . $task['deadline_time']);
        $diffMins = ($deadline->getTimestamp() - $now->getTimestamp()) / 60;

        if ($diffMins < 0)        $score = 1;
        elseif ($diffMins <= 60)  $score = 2;
        elseif ($diffMins <= 180) $score = 3;
        elseif ($diffMins <= 360) $score = 5;
        elseif ($diffMins <= 480) $score = 7;
        else                      $score = 9;

        // Blend with rank among today's tasks
        $finalScore = max(1, min(10, (int) round(($score + $rank + 1) / 2)));

        $upd = $pdo->prepare("UPDATE tasks SET priority_score = ? WHERE id = ?");
        $upd->execute([$finalScore, $task['id']]);
    }
}