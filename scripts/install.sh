#!/usr/bin/env bash
# 安装 agent-skills、agent-commands（Cursor）、agent-slash-skills（Claude/Codex）
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
SKILLS_SRC="${SKILLS_SRC:-$ROOT/agent-skills}"
COMMANDS_SRC="${COMMANDS_SRC:-$ROOT/agent-commands}"
SLASH_SRC="${SLASH_SRC:-$ROOT/agent-slash-skills}"
MODE="link"
SCOPE="user"
TARGETS=()
WHAT="all"
SKIP_DEPS="false"
WITH_ML="false"
INSTALL_DEPS="true"

usage() {
  cat <<'EOF'
用法: scripts/install.sh [选项]

组件:
  agent-skills/       分析 workflow（12 个，含 stock-main 主编排）
  agent-commands/     Cursor 快捷指令（纯 Markdown）
  agent-slash-skills/ Claude/Codex 快捷指令（SKILL.md + /stock 或 $stock）

选项:
  --target TARGET   cursor | claude | codex | agents | all
  --scope SCOPE     user (默认) 或 project
  --what WHAT       skills | commands | slash | all (默认 all)
  --copy            复制而非符号链接
  --unlink          卸载
  --skip-deps       跳过 Python 虚拟环境与 pip 安装
  --with-ml         额外安装 requirements-ml.txt（量化/TCN）
  -h, --help        帮助

默认会自动：创建 .venv → pip install -r requirements.txt → 同步 .cursor/mcp.json

示例:
  bash scripts/install.sh --target all
  bash scripts/install.sh --target claude --what slash

各工具快捷指令用法:
  Cursor      /stock 贵州茅台
  Claude Code /stock 贵州茅台
  Codex CLI   $stock 贵州茅台  或 /skills 选择 stock

安装路径:
  分析 Skills     -> */skills/     (agent-skills)
  Cursor 命令     -> .cursor/commands/  (agent-commands)
  快捷 Skills     -> */skills/     (agent-slash-skills, Claude/Codex/Agents)
EOF
}

skills_dest_for() {
  local agent="$1"
  case "$SCOPE:$agent" in
    user:cursor)      echo "${CURSOR_SKILLS_DIR:-$HOME/.cursor/skills}" ;;
    project:cursor)   echo "$ROOT/.cursor/skills" ;;
    user:claude)      echo "${CLAUDE_SKILLS_DIR:-$HOME/.claude/skills}" ;;
    project:claude)   echo "$ROOT/.claude/skills" ;;
    user:codex)       echo "${CODEX_SKILLS_DIR:-$HOME/.codex/skills}" ;;
    project:codex)    echo "$ROOT/.codex/skills" ;;
    user:agents)      echo "${AGENTS_SKILLS_DIR:-$HOME/.agents/skills}" ;;
    project:agents)   echo "$ROOT/.agents/skills" ;;
    *) echo "未知 target: $agent" >&2; return 1 ;;
  esac
}

commands_dest_for() {
  case "$SCOPE" in
    user)    echo "${CURSOR_COMMANDS_DIR:-$HOME/.cursor/commands}" ;;
    project) echo "$ROOT/.cursor/commands" ;;
    *) echo "未知 scope: $SCOPE" >&2; return 1 ;;
  esac
}

link_dir_entries() {
  local src_dir="$1"
  local dest="$2"
  local require_skill="${3:-false}"
  local label="$4"
  local entry name src_abs
  # 已废弃，不再安装到用户目录
  local skip_names=(
    stock-investment-advisor
    stock-role
  )

  mkdir -p "$dest"

  for entry in "$src_dir"/*; do
    [[ -e "$entry" ]] || continue
    name="$(basename "$entry")"
    local base="$name"
    [[ "$base" == *.md ]] && base="${base%.md}"
    for skip in "${skip_names[@]}"; do
      if [[ "$name" == "$skip" || "$base" == "$skip" ]]; then
        continue 2
      fi
    done
    if [[ "$require_skill" == "true" && ! -f "$entry/SKILL.md" ]]; then
      continue
    fi
    if [[ "$require_skill" == "false" && ! -f "$entry" ]]; then
      continue
    fi
    src_abs="$(cd "$(dirname "$entry")" && pwd)/$name"

    if [[ "$MODE" == "unlink" ]]; then
      if [[ -L "$dest/$name" ]] || [[ -e "$dest/$name" ]]; then
        rm -rf "$dest/$name"
        echo "removed $label: $dest/$name"
      fi
      continue
    fi

    if [[ "$MODE" == "copy" ]]; then
      rm -rf "$dest/$name"
      cp -R "$src_abs" "$dest/$name"
      echo "copied $label:  $dest/$name"
    else
      ln -sfn "$src_abs" "$dest/$name"
      echo "linked $label:  $dest/$name -> $src_abs"
    fi
  done
}

install_skills() {
  link_dir_entries "$SKILLS_SRC" "$1" true "skill"
}

install_slash_skills() {
  link_dir_entries "$SLASH_SRC" "$1" true "slash"
}

install_commands() {
  link_dir_entries "$COMMANDS_SRC" "$1" false "command"
}

remove_deprecated_skills() {
  local dest="$1"
  local name
  local deprecated=(
    stock-investment-advisor
    stock-role
  )
  for name in "${deprecated[@]}"; do
    if [[ -e "$dest/$name" ]]; then
      rm -rf "$dest/$name"
      echo "removed deprecated skill: $dest/$name"
    fi
  done
}

find_python3() {
  if command -v python3 >/dev/null 2>&1; then
    command -v python3
    return 0
  fi
  if command -v python >/dev/null 2>&1; then
    command -v python
    return 0
  fi
  echo "未找到 python3，请先安装 Python 3.10+" >&2
  return 1
}

ensure_project_venv() {
  local py="$1"
  local venv="$ROOT/.venv"
  if [[ ! -x "$venv/bin/python" ]]; then
    echo "[python] 创建虚拟环境: $venv"
    "$py" -m venv "$venv"
  fi
  echo "$venv"
}

install_python_deps() {
  if [[ "$MODE" == "unlink" || "$SKIP_DEPS" == "true" || "$INSTALL_DEPS" != "true" ]]; then
    [[ "$SKIP_DEPS" == "true" ]] && echo "[python] 跳过依赖安装 (--skip-deps)"
    return 0
  fi

  local py venv pip pyexe
  py="$(find_python3)"
  venv="$(ensure_project_venv "$py")"
  pip="$venv/bin/pip"
  pyexe="$venv/bin/python"

  echo "[python] 安装依赖: $ROOT/requirements.txt"
  "$pip" install -q --upgrade pip wheel

  local req_hash_file="$venv/.requirements.sha256"
  local req_hash
  req_hash="$(shasum -a 256 "$ROOT/requirements.txt" | awk '{print $1}')"
  if [[ -f "$req_hash_file" && "$(cat "$req_hash_file")" == "$req_hash" ]]; then
    echo "[python] requirements.txt 未变化，跳过 pip install"
  else
    "$pip" install -q -r "$ROOT/requirements.txt"
    echo "$req_hash" > "$req_hash_file"
  fi

  if [[ "$WITH_ML" == "true" && -f "$ROOT/requirements-ml.txt" ]]; then
    echo "[python] 安装 ML 依赖: $ROOT/requirements-ml.txt"
    "$pip" install -q -r "$ROOT/requirements-ml.txt"
  fi

  echo "[python] 依赖就绪: $pyexe"
  "$pyexe" -c "import browser_cookie3, pysnowball, mcp; print('[python] 校验: browser-cookie3 / pysnowball / mcp OK')" \
    || echo "[python] 警告: 部分包导入失败，请检查上方 pip 输出" >&2
}

sync_cursor_mcp_json() {
  local want_cursor=false
  local agent
  for agent in "$@"; do
    if [[ "$agent" == "cursor" ]]; then
      want_cursor=true
      break
    fi
  done
  [[ "$want_cursor" == "true" ]] || return 0
  [[ "$MODE" == "unlink" ]] && return 0
  [[ -x "$ROOT/.venv/bin/python" ]] || return 0

  "$ROOT/.venv/bin/python" - "$ROOT" <<'PY'
import json
import sys
from pathlib import Path

root = Path(sys.argv[1])
mcp_path = root / ".cursor" / "mcp.json"
example = root / ".cursor" / "mcp.json.example"
pyexe = str(root / ".venv" / "bin" / "python")

data = {}
if mcp_path.is_file():
    data = json.loads(mcp_path.read_text(encoding="utf-8"))
elif example.is_file():
    data = json.loads(example.read_text(encoding="utf-8"))
servers = data.setdefault("mcpServers", {})
servers["eastmoney-stock"] = {
    "command": pyexe,
    "args": ["-m", "mcp_server"],
    "cwd": str(root),
}
mcp_path.parent.mkdir(parents=True, exist_ok=True)
mcp_path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
print(f"[mcp] 已同步 {mcp_path} -> {pyexe}")
PY
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --target) TARGETS+=("${2:-}"); shift 2 ;;
    --scope)  SCOPE="${2:-}"; shift 2 ;;
    --what)   WHAT="${2:-}"; shift 2 ;;
    --copy)   MODE="copy"; shift ;;
    --unlink) MODE="unlink"; shift ;;
    --skip-deps) SKIP_DEPS="true"; shift ;;
    --with-ml) WITH_ML="true"; shift ;;
    -h|--help) usage; exit 0 ;;
    *) echo "未知参数: $1" >&2; usage; exit 1 ;;
  esac
done

if [[ ${#TARGETS[@]} -eq 0 ]]; then
  TARGETS=(all)
fi

if [[ "$WHAT" != "skills" && "$WHAT" != "commands" && "$WHAT" != "slash" && "$WHAT" != "all" ]]; then
  echo "--what 必须是 skills、commands、slash 或 all" >&2
  exit 1
fi

if [[ "$WHAT" == "skills" || "$WHAT" == "all" ]] && [[ ! -d "$SKILLS_SRC" ]]; then
  echo "未找到: $SKILLS_SRC" >&2; exit 1
fi
if [[ "$WHAT" == "commands" || "$WHAT" == "all" ]] && [[ ! -d "$COMMANDS_SRC" ]]; then
  echo "未找到: $COMMANDS_SRC" >&2; exit 1
fi
if [[ "$WHAT" == "slash" || "$WHAT" == "all" ]] && [[ ! -d "$SLASH_SRC" ]]; then
  echo "未找到: $SLASH_SRC" >&2; exit 1
fi

if [[ "$SCOPE" != "user" && "$SCOPE" != "project" ]]; then
  echo "--scope 必须是 user 或 project" >&2; exit 1
fi

expanded=()
for t in "${TARGETS[@]}"; do
  if [[ "$t" == "all" ]]; then
    expanded+=(cursor claude codex agents)
  else
    expanded+=("$t")
  fi
done

echo "分析 Skills: $SKILLS_SRC"
echo "Cursor 命令: $COMMANDS_SRC"
echo "快捷 Skills: $SLASH_SRC"
echo "模式: $MODE | 范围: $SCOPE | 组件: $WHAT"
echo "---"

install_python_deps
sync_cursor_mcp_json "${expanded[@]}"
echo "---"

for agent in "${expanded[@]}"; do
  if [[ "$WHAT" == "skills" || "$WHAT" == "all" ]]; then
    dest="$(skills_dest_for "$agent")"
    echo "[$agent 分析 skills] -> $dest"
    remove_deprecated_skills "$dest"
    install_skills "$dest"
  fi

  if [[ "$WHAT" == "slash" || "$WHAT" == "all" ]]; then
    if [[ "$agent" == "cursor" ]]; then
      echo "[cursor slash] 跳过（Cursor 使用 agent-commands/）"
    else
      dest="$(skills_dest_for "$agent")"
      echo "[$agent 快捷 slash] -> $dest"
      install_slash_skills "$dest"
    fi
  fi

  if [[ "$WHAT" == "commands" || "$WHAT" == "all" ]]; then
    if [[ "$agent" != "cursor" ]]; then
      echo "[$agent commands] 跳过（非 Cursor）"
    else
      dest="$(commands_dest_for)"
      echo "[cursor commands] -> $dest"
      install_commands "$dest"
    fi
  fi
  echo
done

if [[ "$MODE" == "unlink" ]]; then
  echo "卸载完成。"
else
  cat <<EOF
安装完成。

Python: $ROOT/.venv/bin/python（MCP eastmoney-stock 已指向此环境）
快捷指令:
  Cursor:      /stock 贵州茅台
  Claude Code: /stock 贵州茅台
  Codex:       \$stock 贵州茅台

请重启 Cursor 使 MCP / Skills 生效。
EOF
fi
