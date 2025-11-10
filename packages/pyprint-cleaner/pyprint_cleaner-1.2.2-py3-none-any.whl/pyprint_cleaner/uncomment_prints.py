import os
import shutil

def get_backup_dir(project_dir):
    """Return backup folder path inside project."""
    return os.path.join(project_dir, ".print_backups")


def restore_auto_commented_prints(root_dir, dry_run=False):
    """
    Restore lines commented as '# [auto] print(' from their .bak backups.
    Does NOT overwrite the whole file — only restores prints safely.
    """
    backup_dir = get_backup_dir(root_dir)
    if not os.path.exists(backup_dir):
        print("⚠️ No backup folder found — nothing to restore.")
        return

    restored_files = 0
    restored_lines_total = 0

    for filename in os.listdir(backup_dir):
        if not filename.endswith(".bak"):
            continue

        backup_path = os.path.join(backup_dir, filename)
        original_name = filename[:-4]  # remove .bak

        # Find original file in project
        for subdir, _, files in os.walk(root_dir):
            if backup_dir in subdir:
                continue
            if original_name in files:
                dest_path = os.path.join(subdir, original_name)

                with open(dest_path, "r", encoding="utf-8") as f:
                    current_lines = f.readlines()
                with open(backup_path, "r", encoding="utf-8") as f:
                    backup_lines = f.readlines()

                # Safely restore matching lines
                new_lines = []
                restored_count = 0

                for i, line in enumerate(current_lines):
                    if line.strip().startswith("# [auto] print("):
                        if i < len(backup_lines):
                            new_line = backup_lines[i]
                            new_lines.append(new_line)
                            restored_count += 1
                        else:
                            new_lines.append(line)  # fallback
                    else:
                        new_lines.append(line)

                if restored_count > 0:
                    restored_files += 1
                    restored_lines_total += restored_count
                    if not dry_run:
                        with open(dest_path, "w", encoding="utf-8") as f:
                            f.writelines(new_lines)
                    print(f"♻️ Restored {restored_count} print(s) in: {dest_path}")

                break  # move to next file

    if restored_files == 0:
        print("⚠️ No files with # [auto] print( lines found to restore.")
    else:
        print(f"✅ Restored {restored_lines_total} print(s) across {restored_files} file(s).")


def uncomment_prints():
    project_dir = os.getcwd()
    dry_run = False  # set True to preview changes
    restore_auto_commented_prints(project_dir, dry_run=dry_run)


def main():
    """CLI entry point for `uncomment-prints` command."""
    uncomment_prints()


if __name__ == "__main__":
    main()
