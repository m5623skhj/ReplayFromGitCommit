# Commit Replay Tool

Git 커밋을 재현하고 비교할 수 있는 도구입니다.  
특정 커밋을 빌드하고 실행하여 로그를 저장하거나, 두 커밋의 빌드 결과를 비교할 수 있습니다. 또한 worktree를 관리할 수 있습니다.

## 주요 기능

### 1. reproduce
특정 커밋을 재현하고 로그를 저장합니다.

- **빌드 → 실행 → 로그 저장** 순으로 수행
- 사용 예시:
```bash
> reproduce f155d1b
```
- 로그 파일: `logs/f155d1b.log`
- 로그 태그:
  - `[BUILD]` : 빌드 명령 실행
  - `[RUN]` : 실행 명령 실행

### 2. compare
두 커밋을 비교하여 로그 차이를 확인합니다.

- 각 커밋 worktree 생성 → 빌드 → 실행 → 로그 저장
- 로그 파일 비교: `diff -u logs/compare_<commit1>.log logs/compare_<commit2>.log`
- 사용 예시:
```bash
> compare f155d1b a12b3c4
```
- 로그 태그:
  - `[BUILD]` : 각 커밋 빌드
  - `[RUN]` : 각 커밋 실행
  - `[DONE]` : 로그 저장 완료 표시

### 3. cleanup
worktree를 제거합니다.

- 특정 커밋 worktree 삭제:
```bash
> cleanup f155d1b
```
- 모든 worktree 삭제:
```bash
> cleanup all
```
- 로그 태그:
  - `[CLEANUP]` : worktree 삭제 실행

### 4. help
도움말을 출력합니다.

```bash
> help
```

### 5. exit
프로그램 종료

```bash
> exit
```

## 디렉토리 구조

```
.
├─ replay.py           # 메인 REPL 스크립트
├─ config.json         # 빌드/실행 명령어 설정
├─ logs/               # 실행 로그 저장
└─ worktrees/          # 커밋별 worktree 저장
```

## config.json 예시

```json
{
    "build_command": "msbuild ../ReplayTest/ReplayTest.sln /p:Configuration=Debug",
    "run_command": "../ReplayTest/x64/Debug/ReplayTest.exe"
}
```

- `build_command` : 커밋 worktree 빌드 명령
- `run_command` : 빌드 후 실행 명령

## 로그 태그 설명

| 태그        | 의미 |
|------------|------|
| `[BUILD]`  | 빌드 명령 실행 |
| `[RUN]`    | 실행 명령 실행 |
| `[CLEANUP]`| worktree 삭제 실행 |
| `[INFO]`   | 일반 정보 출력 |
| `[DONE]`   | 작업 완료 표시 |
| `[ERROR]`  | 오류 발생 시 표시 |
