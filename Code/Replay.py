import subprocess
import json
from pathlib import Path

CONFIG_FILE = "config.json"
LOG_DIR = Path("logs")
WORKTREE_DIR = Path("worktrees")
LOG_DIR.mkdir(exist_ok=True)
WORKTREE_DIR.mkdir(exist_ok=True)


def load_config():
    if not Path(CONFIG_FILE).exists():
        raise FileNotFoundError(f"{CONFIG_FILE} 파일이 없습니다.")
    with open(CONFIG_FILE, "r") as f:
        return json.load(f)


def run_command(cmd, cwd=None, log_file=None, tag="[RUN]"):
    print(f"{tag} {cmd} (cwd={cwd})")
    if log_file:
        with open(log_file, "w") as f:
            subprocess.run(cmd, shell=True, stdout=f, stderr=subprocess.STDOUT, text=True, cwd=cwd)
    else:
        subprocess.run(cmd, shell=True, text=True, cwd=cwd)


def prepare_worktree(commit):
    target_dir = WORKTREE_DIR / commit
    if target_dir.exists():
        print(f"[INFO] worktree {target_dir} 이미 존재, 재사용")
        return target_dir

    print(f"[INFO] worktree 생성: {target_dir}")
    run_command(f"git worktree add {target_dir} {commit}", tag="[CLEANUP]")
    return target_dir


def cleanup_worktree(commit):
    if commit.lower() == "all":
        print(f"[INFO] 모든 worktree 삭제 시도")
        for wt_dir in WORKTREE_DIR.iterdir():
            if wt_dir.is_dir():
                run_command(f"git worktree remove {wt_dir} --force", tag="[CLEANUP]")
        print("[DONE] 모든 worktree 삭제 완료")
        return

    target_dir = WORKTREE_DIR / commit
    if target_dir.exists():
        print(f"[INFO] worktree {target_dir} 삭제 시도")
        run_command(f"git worktree remove {target_dir} --force", tag="[CLEANUP]")
    else:
        print(f"[INFO] worktree {target_dir} 없음, 삭제 건너뜀")


def reproduce_commit(commit, config):
    print(f"[INFO] Commit {commit} 실행 시작")
    wt_dir = prepare_worktree(commit)
    run_command(config["build_command"], cwd=wt_dir, tag="[BUILD]")
    log_file = LOG_DIR / f"{commit}.log"
    run_command(config["run_command"], cwd=wt_dir, log_file=log_file, tag="[RUN]")
    print(f"[DONE] 로그 저장: {log_file}")


def compare_commits(commit1, commit2, config):
    print(f"[INFO] {commit1} vs {commit2} 비교 실행")
    for commit in [commit1, commit2]:
        wt_dir = prepare_worktree(commit)
        run_command(config["build_command"], cwd=wt_dir, tag="[BUILD]")
        log_file = LOG_DIR / f"compare_{commit}.log"
        run_command(config["run_command"], cwd=wt_dir, log_file=log_file, tag="[RUN]")
        print(f"[DONE] {commit} 로그: {log_file}")

    subprocess.run(
        ["diff", "-u",
         str(LOG_DIR / f"compare_{commit1}.log"),
         str(LOG_DIR / f"compare_{commit2}.log")]
    )


def print_help():
    print("""
=== Commit Replay Tool 명령어 ===
reproduce <commit>         : 특정 커밋 재현, 빌드 및 실행 후 로그 저장
compare <commit1> <commit2>: 두 커밋 빌드 및 실행 후 로그 diff
cleanup <commit|all>       : 특정 커밋 또는 모든 worktree 삭제
help                       : 도움말 출력
exit                       : 프로그램 종료
""")


def repl():
    config = load_config()
    print("=== Commit Replay Tool ===")
    print("명령어를 입력하세요.")
    print("종료하려면 'exit' 입력, 도움말은 'help' 입력")

    while True:
        try:
            cmd_input = input("> ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\n[EXIT] 종료합니다.")
            break

        if not cmd_input:
            continue

        cmd_parts = cmd_input.split()
        cmd = cmd_parts[0].lower()

        if cmd == "exit":
            print("[EXIT] 종료합니다.")
            break
        elif cmd == "help":
            print_help()
            continue

        try:
            if cmd == "reproduce":
                if len(cmd_parts) < 2:
                    print("[ERROR] 커밋 해시를 지정해야 합니다.")
                    continue
                commit = cmd_parts[1]
                reproduce_commit(commit, config)

            elif cmd == "compare":
                if len(cmd_parts) < 3:
                    print("[ERROR] 두 개의 커밋 해시를 지정해야 합니다.")
                    continue
                commit1, commit2 = cmd_parts[1], cmd_parts[2]
                compare_commits(commit1, commit2, config)

            elif cmd == "cleanup":
                if len(cmd_parts) < 2:
                    print("[ERROR] 커밋 해시 또는 'all'을 지정해야 합니다.")
                    continue
                commit = cmd_parts[1]
                cleanup_worktree(commit)

            else:
                print(f"[ERROR] 알 수 없는 명령어: {cmd}. 'help' 입력으로 확인하세요.")

        except Exception as e:
            print(f"[ERROR] 명령 실행 중 오류 발생: {e}")


if __name__ == "__main__":
    repl()
