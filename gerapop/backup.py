"""CLI de backup dos POPs gerados: python -m gerapop.backup"""

from datetime import datetime

from gerapop.storage import gerar_backup_zip, get_storage_dir


def main() -> None:
    backup_dir = get_storage_dir() / "backups"
    backup_dir.mkdir(parents=True, exist_ok=True)
    filename = f"gerapop_{datetime.now().strftime('%Y%m%d_%H%M%S')}.zip"
    target = backup_dir / filename
    target.write_bytes(gerar_backup_zip())
    print(f"Backup salvo em {target} ({target.stat().st_size} bytes)")


if __name__ == "__main__":
    main()
