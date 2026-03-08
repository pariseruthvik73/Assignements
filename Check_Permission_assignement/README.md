# Assignment 1: File Permission Checker — Shell Scripting

## 1. Project Overview

This project implements a Bash shell script called `check_permissions.sh` that helps system administrators verify file and directory permissions on a Linux system. The script checks ownership, detects security vulnerabilities like world-writable files, and reports results with color-coded output and proper exit codes.

Student: Ruthvik Parise  
Tech Stack: Bash, Linux (Ubuntu/Amazon Linux), Git, GitHub Codespaces  
Script: `check_permissions.sh`

---

## 2. Setting Up the Project

### Create Folder Structure

All directories and files were created using a single command from the parent directory:

```bash
cd .. && mkdir -p app static/{css,js} && touch app/{api.php,db.php}
```

Breakdown:
- `cd ..` — navigate back one directory
- `&&` — chain commands (next runs only if previous succeeds)
- `mkdir -p` — create directories (`-p` avoids error if exists)
- `touch app/{api.php,db.php}` — create both PHP files using brace expansion

Verify structure:

```bash
tree
```

Expected output:

```
.
├── app
│   ├── api.php
│   └── db.php
├── check_permissions.sh
└── static
    ├── css
    └── js
```

---

## 3. The Script

### Make It Executable

```bash
chmod +x check_permissions.sh
```

### Usage

```bash
./check_permissions.sh <file_or_directory> <expected_permissions>
```

### Examples

```bash
# Check a directory expects 755
./check_permissions.sh app 755

# Check PHP files expect 644
./check_permissions.sh app/api.php 644
./check_permissions.sh app/db.php 644

# Check static folders
./check_permissions.sh static 755
./check_permissions.sh static/css 755
```

---

## 4. What the Script Checks

### Argument Validation

```bash
if [ $# -ne 2 ]; then
    echo "❌ Usage: $0 <file/directory> <expected_permissions>"
    exit 3
fi
```

Requires exactly 2 arguments — path and expected permission. Validates permission format using regex: `^[0-7]{3,4}$`. Exit code `3` for invalid arguments.

### File Existence Check

```bash
if [ ! -e "$TARGET" ]; then
    echo "❌ '$TARGET' does not exist"
    exit 2
fi
```

Uses `-e` flag to test if path exists. Exit code `2` for file not found.

### Permission Comparison

```bash
ACTUAL=$(stat -c %a "$TARGET")

if [ "$ACTUAL" == "$EXPECTED" ]; then
    echo "✅ $TARGET has correct permissions ($ACTUAL)"
else
    echo "❌ $TARGET has permissions $ACTUAL (expected $EXPECTED)"
fi
```

`stat -c %a` extracts current octal permissions and compares actual vs expected.

### Ownership Check

```bash
OWNER=$(stat -c %U "$TARGET")
CURRENT_USER=$(whoami)

if [ "$OWNER" == "$CURRENT_USER" ]; then
    echo "✅ File ownership is secure"
else
    echo "❌ File owned by '$OWNER', not current user '$CURRENT_USER'"
fi
```

`stat -c %U` gets the file owner username. `whoami` gets the currently logged-in user.

### Security Analysis

```bash
# World-writable check
LAST_DIGIT="${ACTUAL: -1}"
if [[ "$LAST_DIGIT" == "2" || "$LAST_DIGIT" == "6" || "$LAST_DIGIT" == "7" ]]; then
    echo "⚠️  WARNING: File is world-writable!"
fi

# SUID/SGID check
if [ ${#FULL_PERM} -eq 4 ]; then
    echo "⚠️  WARNING: SUID/SGID bit is set!"
fi
```

Dangerous permission patterns detected:
- World-writable — last octal digit is 2, 3, 6, or 7
- World-executable — last octal digit is 1, 3, 5, or 7
- SUID/SGID — 4-digit octal with leading 4, 6, or 7

---

## 5. Exit Codes

| Code | Meaning |
|------|---------|
| `0` | All checks passed |
| `1` | Permission mismatch or security issue found |
| `2` | File or directory not found |
| `3` | Invalid arguments or bad permission format |

---

## 6. Sample Output

### Good Case (permissions match)

```
── Checking: app/api.php ──
   📁 Type       : File
   🔑 Permissions: 644 (expected: 644)
   👤 Owner      : codespace (current user: codespace)

── Permission Check ──
✅ app/api.php has correct permissions (644)

── Ownership Check ──
✅ File ownership is secure (owned by codespace)

── Security Analysis ──
✅ Not world-writable
✅ Not world-executable
✅ No SUID/SGID bits set

── Detailed Info (ls -l) ──
-rw-r--r-- 1 codespace codespace 0 Mar 8 13:04 app/api.php

✅ All checks passed for 'app/api.php'
Exit code: 0
```

### Bad Case (world-writable file detected)

```
── Checking: app/db.php ──
   📁 Type       : File
   🔑 Permissions: 666 (expected: 644)
   👤 Owner      : codespace (current user: codespace)

── Permission Check ──
❌ app/db.php has permissions 666 (expected 644)

── Security Analysis ──
⚠️  WARNING: 'app/db.php' is world-writable! (permissions: 666)

── Detailed Info (ls -l) ──
-rw-rw-rw- 1 codespace codespace 0 Mar 8 13:04 app/db.php

❌ One or more checks failed for 'app/db.php'
Exit code: 1
```

---

## 7. Fixing Permissions

If the script reports a security issue, fix it with `chmod`:

```bash
# Fix world-writable file
chmod 644 app/db.php

# Verify fix
./check_permissions.sh app/db.php 644
```

---

## 8. Troubleshooting

### Script Not Running — Permission Denied

```
bash: ./check_permissions.sh: Permission denied
```

Fix:

```bash
chmod +x check_permissions.sh
```

### Running `./` Without Filename

```
bash: ./: Is a directory
```

Fix — always include the script name:

```bash
./check_permissions.sh app 755   # ✅ correct
./                               # ❌ wrong
```

### Missing Arguments

```
❌ Usage: ./check_permissions.sh <file/directory> <expected_permissions>
```

Fix — always pass both path AND permission:

```bash
./check_permissions.sh app/db.php 644   # ✅ correct
./check_permissions.sh app/db.php       # ❌ missing second argument
```

---

## 9. Key Concepts Learned

### Command-Line Arguments

```bash
$1     # First argument  (file path)
$2     # Second argument (expected permission)
$#     # Total number of arguments passed
$0     # Script name itself
```

### File Test Operators

| Operator | Meaning |
|----------|---------|
| `-e` | Path exists (file or directory) |
| `-f` | Is a regular file |
| `-d` | Is a directory |

### `stat` Command

```bash
stat -c %a filename    # Get octal permissions (e.g., 644)
stat -c %U filename    # Get owner username
```

### Brace Expansion

```bash
touch app/{api.php,db.php}
# Equivalent to:
touch app/api.php app/db.php
```

Creates multiple files or directories in one command. Works with nested paths:

```bash
mkdir -p static/{css,js}    # Creates static/css and static/js
```

### Exit Codes

Exit codes allow scripts to communicate status to other scripts or CI/CD pipelines:

```bash
exit 0   # Success
exit 1   # Failure
exit 2   # File not found
exit 3   # Bad arguments
```

Check exit code of last command:

```bash
echo $?   # Prints 0, 1, 2, or 3
```

### String Manipulation in Bash

```bash
LAST_DIGIT="${ACTUAL: -1}"    # Get last character
LENGTH="${#FULL_PERM}"        # Get string length
```

---

## 10. Running the Complete Test

```bash
cd /workspaces/Assignements/Assignement_1\(Shell_script\)
chmod +x check_permissions.sh

# Run all checks
./check_permissions.sh app 755
./check_permissions.sh app/api.php 644
./check_permissions.sh app/db.php 644
./check_permissions.sh static 755
./check_permissions.sh static/css 755
./check_permissions.sh static/js 755
```

---

## 11. Script Logic Flow

```
1. Validate arguments (2 required)
   ├─ Missing args? → Exit 3
   └─ Invalid format? → Exit 3

2. Check file exists
   ├─ Not found? → Exit 2
   └─ Found → Continue

3. Get actual permissions (stat -c %a)

4. Compare actual vs expected
   ├─ Mismatch? → Flag error
   └─ Match → Continue

5. Check ownership (stat -c %U vs whoami)
   ├─ Different owner? → Flag warning
   └─ Same owner → Continue

6. Security analysis
   ├─ World-writable? → Flag warning
   ├─ World-executable? → Flag warning
   └─ SUID/SGID? → Flag warning

7. Return exit code
   ├─ Any flags? → Exit 1
   └─ All passed → Exit 0
```

---

## 12. Real-World Applications

This type of permission checking is used in:

1. **Security Audits** — automated scanning for misconfigured files
2. **CI/CD Pipelines** — verify deployment permissions before release
3. **Compliance Checks** — ensure files meet security standards (PCI-DSS, SOC2)
4. **Infrastructure as Code** — validate Terraform/Ansible file permissions
5. **Container Security** — check Dockerfile and config file permissions

---

## 13. Conclusion

This assignment successfully demonstrated:

1. Writing a production-grade Bash shell script from scratch
2. Handling command-line arguments with validation
3. Using `stat`, `chmod`, `whoami`, and `ls` for file inspection
4. Detecting dangerous permission patterns (world-writable, SUID/SGID)
5. Implementing meaningful exit codes for scripting pipelines
6. Brace expansion for efficient file/folder creation

Key Takeaway: The same principles used here — checking ownership, validating access levels, and reporting misconfigurations — are foundational to DevOps security tooling used in real production environments. Understanding file permissions is critical for securing servers, containers, and cloud infrastructure.

---

*Assignment 1 — Shell Scripting | File Permission Checker | March 2026*
