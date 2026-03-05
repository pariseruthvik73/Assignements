<?php
/**
 * Database Connection
 * Connects to PostgreSQL using environment variables
 */

$host     = getenv('DB_HOST')     ?: 'db';
$port     = getenv('DB_PORT')     ?: '5432';
$dbname   = getenv('DB_NAME')     ?: 'dayflow';
$user     = getenv('DB_USER')     ?: 'postgres';
$password = getenv('DB_PASSWORD') ?: 'postgres';

$dsn = "pgsql:host={$host};port={$port};dbname={$dbname}";

try {
    $pdo = new PDO($dsn, $user, $password, [
        PDO::ATTR_ERRMODE            => PDO::ERRMODE_EXCEPTION,
        PDO::ATTR_DEFAULT_FETCH_MODE => PDO::FETCH_ASSOC,
        PDO::ATTR_EMULATE_PREPARES   => false,
    ]);

    // Create tasks table if it doesn't exist
    $pdo->exec("
        CREATE TABLE IF NOT EXISTS tasks (
            id              SERIAL PRIMARY KEY,
            task_date       DATE NOT NULL DEFAULT CURRENT_DATE,
            description     VARCHAR(300) NOT NULL,
            dependencies    VARCHAR(200),
            deadline_time   TIME NOT NULL,
            status          VARCHAR(20) NOT NULL DEFAULT 'not_started'
                            CHECK (status IN ('not_started','in_progress','blocked','completed')),
            status_notes    VARCHAR(300),
            priority_score  INTEGER,
            created_at      TIMESTAMP NOT NULL DEFAULT NOW(),
            updated_at      TIMESTAMP NOT NULL DEFAULT NOW()
        );

        CREATE INDEX IF NOT EXISTS idx_tasks_date ON tasks(task_date);
    ");

} catch (PDOException $e) {
    // Let calling code handle the error
    throw $e;
}