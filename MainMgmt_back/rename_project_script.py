import os
from pathlib import Path


def rename_project(old_name="rbac_demo", new_name="mainmgmt"):
    """智能重命名项目，自动跳过二进制文件和缓存目录"""

    project_path = Path(".")

    # 需要处理的文件后缀
    text_extensions = {
        '.py', '.yaml', '.yml', '.json', '.md', '.txt', '.ini', '.cfg',
        '.toml', '.sh', '.env', '.example', '.conf', '.ini', '.html',
        '.css', '.js', '.ts', '.vue', '.jsx', '.tsx', '.sql', '.log'
    }

    # 需要跳过的目录
    skip_dirs = {
        '__pycache__', '.git', 'node_modules', 'venv', 'env',
        '.venv', '.env', 'dist', 'build', '.pytest_cache'
    }

    # 需要跳过的文件后缀（二进制文件）
    skip_extensions = {
        '.pyc', '.pyo', '.pyd', '.so', '.dll', '.exe',
        '.png', '.jpg', '.jpeg', '.gif', '.bmp', '.ico',
        '.zip', '.tar', '.gz', '.7z', '.rar',
        '.pdf', '.doc', '.docx', '.xls', '.xlsx',
        '.db', '.sqlite', '.sqlite3'
    }

    processed_files = []
    skipped_files = []

    # 遍历所有文件
    for file_path in project_path.rglob("*"):
        if file_path.is_file():
            # 检查是否需要跳过
            if any(skip_dir in file_path.parts for skip_dir in skip_dirs):
                skipped_files.append(f"跳过缓存目录: {file_path}")
                continue

            if file_path.suffix.lower() in skip_extensions:
                skipped_files.append(f"跳过二进制文件: {file_path}")
                continue

            if file_path.suffix.lower() not in text_extensions:
                skipped_files.append(f"跳过未知类型: {file_path}")
                continue

            # 处理文本文件
            try:
                content = file_path.read_text(encoding='utf-8', errors='ignore')
                if old_name in content:
                    new_content = content.replace(old_name, new_name)
                    file_path.write_text(new_content, encoding='utf-8')
                    processed_files.append(f"✓ 已更新: {file_path}")
                else:
                    skipped_files.append(f"无需更新: {file_path}")
            except Exception as e:
                skipped_files.append(f"✗ 读取失败: {file_path} - {e}")

    # 打印结果
    print("\n" + "=" * 60)
    print(f"处理完成！")
    print("=" * 60)
    print(f"\n📄 成功更新 {len(processed_files)} 个文件:")
    for msg in processed_files:
        print(msg)

    print(f"\n⏭️  跳过 {len(skipped_files)} 个文件/目录")
    print("（这些是缓存文件、二进制文件或不含旧名称的文件）")

    # 关键文件检查清单
    print("\n" + "=" * 60)
    print("⚠️  请手动检查以下关键文件：")
    print("=" * 60)
    check_files = [
        "manage.py",
        f"{new_name}/settings.py",
        f"{new_name}/wsgi.py",
        f"{new_name}/asgi.py",
        "docker-compose.yml",
        ".env"
    ]

    for check_file in check_files:
        if Path(check_file).exists():
            content = Path(check_file).read_text(encoding='utf-8')
            if old_name not in content:
                print(f"✅ {check_file}")
            else:
                print(f"❌ {check_file} - 仍包含旧名称")
        else:
            print(f"⚠️  {check_file} - 文件不存在")


if __name__ == "__main__":
    rename_project()