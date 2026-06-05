# PSA-Error-Collection-System

# About the project

# Features

# Authors

# How to Navigate?

and such 

[ feel free to edit this ]

----------------------------
# GUIDE TO MAKE PULL REQUEST 
[delete this part later]

## How to sync from github version to your local version
Since 1 groupname made changes, lets sync it to our local version
Also, this added guide must be synced in your local repository also

From google:
To sync a GitHub version to your local version in Visual Studio Code (VS Code), you can click the "Sync Changes" button in the Source Control panel. This action automatically runs a git pull followed by a git push to synchronize both environments.

## Changes vs Staged Changes in VS Code

Think of Git as having **3 areas**:

### 1. Working Directory (Changes)

These are files you've edited but Git is only noticing them.

```
Changes
 ├─ birth_table.sql
 ├─ person_table.sql
 └─ README.md
```

Nothing is prepared for a commit yet.

Example:

* You modify `person_table.sql`
* VS Code shows it under **Changes**
* Git knows it changed, but it won't be included in the next commit unless staged

---

### 2. Staging Area (Staged Changes)

When you click the **+** button beside a file, you tell Git:

> "Include this file in my next commit."

```
Staged Changes
 ├─ person_table.sql
 └─ README.md
```

Now those files are ready to be committed.

---

### 3. Commit

Enter a message:
- a whol but short description of what you changed

```
Example:
Added foreign key constraints
```

and clicking **Commit**, Git creates a snapshot containing only the staged files.

---

### Example

Suppose you changed:

```
person.sql
birth.sql
README.md
```

But you only want to commit `person.sql`.

Stage only:

```
person.sql
```

Result:

```
Staged Changes
 └─ person.sql

Changes
 ├─ birth.sql
 └─ README.md
```

When you commit, only `person.sql` goes into that commit.

---


# NOW, THIS IS FOR PULLING / PUSHING FOR OUR GROUP
 ## Important Rule
> Never work directly on `main` branch.

## IF First Time Only

Open VSC, and open Terminal

Then,
Clone repository:

```bash
git clone <repo-url link>
```

Open in VS Code.

---

## Before Starting Any New Task

### Step 1: Pull Latest Main

Open Terminal:

```bash
git checkout main
git pull origin main
```

This ensures you are starting from the NEWEST version. 
why? because one of our groupmates made changes, u must sync with ur local version

---

### Step 2: Create Branch

Use a descriptive name.

Examples:

```bash
git checkout -b feature-birth-records
```

or

```bash
git checkout -b fix-import-errors
```

or

```bash
git checkout -b feature-person-table
```

The `-b` means:

> Create branch and switch to it.

---

### Step 3: Verify Branch

In VS Code:

Bottom-left corner should show:

```
feature-birth-records
```

instead of

```
main
```

---

### Step 4: Make Changes

Edit files normally.

---

### Step 5: Stage Files

Source Control tab:

* Click **+** beside changed files
* Files move to **Staged Changes**

---

### Step 6: Commit

Type message:

```
Added birth certificate table
```

Click **Commit**.

---

### Step 7: Push Branch

Click **Publish Branch**

or:

```bash
git push -u origin feature-birth-records
```

Only needed once per branch.

---

### Step 8: Create Pull Request

GitHub usually shows:

```
Compare & Pull Request 
```

Click it.

Add description.

Submit.

---

### Step 9: Wait for Review

Do **not** merge yourself (unless assigned).

The repository owner reviews and merges.
Your changes must be reviewed, before merging it to main
Because what if your code has some fatal error for the system
then, it will break the whole system, and we have to fix it immediately, 
which is a waste of time for everyone

---

## THIS PART IS FOR PEOPLE WHO ARE NOT COMFORTABLE WITH TERMINAL
## Easiest VS Code Method (No Terminal)

1. Click current branch name in bottom-left.
2. Select **Create New Branch**.
3. Enter:

```
feature-birth-records
```

4. Press Enter.
5. VS Code automatically switches to the new branch.
6. Make changes.
7. Commit.
8. Click **Publish Branch**.
9. Open Pull Request.

This is probably the easiest process for classmates who aren't comfortable with Git commands.

### Team Rule

Every task = new branch.

Good:

```
feature-person-table
feature-registry-import
fix-foreign-key
fix-sql-errors
```

Bad:

```
mybranch
test
newbranch
branch1
```