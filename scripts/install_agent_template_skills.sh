#!/bin/sh
set -eu

usage() {
  cat <<'USAGE'
Usage: install_agent_template_skills.sh [--repo PATH] [--agent NAME]... [--mode copy|symlink] [--apply] [--uninstall]

Agents:
  openai, codex          install to ${HOME}/.agents/skills and link into Codex
  claude, claude-code    link into Claude Code
  opencode              link into OpenCode
  copilot, github-copilot link into GitHub Copilot
  gemini                link into Gemini CLI
  openclaw              link into OpenClaw
  all             all known agents

Selected skills are always installed first into ${HOME}/.agents/skills. Agent-specific
skill directories receive symlinks to that canonical location.

Dry run is the default. Add --apply to install or uninstall.
USAGE
}

repo_arg="."
mode="copy"
apply="false"
action="install"
agents=""
newline='
'

while [ "$#" -gt 0 ]; do
  case "${1}" in
    --repo)
      [ "$#" -ge 2 ] || { echo "Missing value for --repo" >&2; exit 2; }
      repo_arg=${2}
      shift 2
      ;;
    --agent)
      [ "$#" -ge 2 ] || { echo "Missing value for --agent" >&2; exit 2; }
      agents="${agents}${agents:+ }${2}"
      shift 2
      ;;
    --mode)
      [ "$#" -ge 2 ] || { echo "Missing value for --mode" >&2; exit 2; }
      mode=${2}
      case "${mode}" in
        copy|symlink) ;;
        *) echo "Invalid --mode: ${mode}" >&2; exit 2 ;;
      esac
      shift 2
      ;;
    --apply)
      apply="true"
      shift
      ;;
    --uninstall)
      action="uninstall"
      shift
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      echo "Unknown argument: ${1}" >&2
      usage >&2
      exit 2
      ;;
  esac
done

prompt_agents() {
  if [ ! -t 0 ]; then
    printf '%s\n' "openai"
    return 0
  fi

  printf '%s\n' "Select agents to install skills for:"
  printf '%s\n' "  1) OpenAI/Codex (~/.agents/skills + ~/.codex/skills)"
  printf '%s\n' "  2) Claude Code (~/.claude/skills)"
  printf '%s\n' "  3) OpenCode (~/.config/opencode/skills)"
  printf '%s\n' "  4) all"
  printf '%s' "Enter numbers or names separated by spaces [openai]: "
  read -r answer || answer=""
  [ -n "${answer}" ] || answer="openai"

  selected=""
  for item in ${answer}; do
    case "${item}" in
      1) selected="${selected}${selected:+ }openai" ;;
      2) selected="${selected}${selected:+ }claude" ;;
      3) selected="${selected}${selected:+ }opencode" ;;
      4) selected="${selected}${selected:+ }all" ;;
      *) selected="${selected}${selected:+ }${item}" ;;
    esac
  done
  printf '%s\n' "${selected}"
}

[ -n "${agents}" ] || agents=$(prompt_agents)

parent_dir() {
  dirname -- "${1}"
}

abspath() {
  case "${1}" in
    /*)
      target_path=${1}
      ;;
    *)
      current_dir=$(pwd)
      target_path="${current_dir}/${1}"
      ;;
  esac
  if [ -d "${target_path}" ]; then
    (cd -- "${target_path}" && pwd)
  else
    path_parent=$(parent_dir "${target_path}")
    path_name=$(basename -- "${target_path}")
    absolute_parent=$(cd -- "${path_parent}" && pwd)
    printf '%s/%s\n' "${absolute_parent}" "${path_name}"
  fi
}

find_repo() {
  if [ -n "${AGENTS_TEMPLATE_REPO:-}" ]; then
    abspath "${AGENTS_TEMPLATE_REPO}"
    return 0
  fi

  candidate=$(abspath "${repo_arg}")
  while :; do
    if [ -f "${candidate}/templates.yml" ] && [ -d "${candidate}/skills" ]; then
      printf '%s\n' "${candidate}"
      return 0
    fi
    [ "${candidate}" != "/" ] || break
    candidate=$(parent_dir "${candidate}")
  done

  script_parent=$(parent_dir "${0}")
  script_dir=$(cd -- "${script_parent}" && pwd)
  candidate=${script_dir}
  while :; do
    if [ -f "${candidate}/templates.yml" ] && [ -d "${candidate}/skills" ]; then
      printf '%s\n' "${candidate}"
      return 0
    fi
    [ "${candidate}" != "/" ] || break
    candidate=$(parent_dir "${candidate}")
  done

  echo "Could not find agents-file-templates-and-skills. Run from the repo or set AGENTS_TEMPLATE_REPO." >&2
  exit 1
}

add_dest() {
  dest=${1}
  case "${newline}${link_destinations}${newline}" in
    *"${newline}${dest}${newline}"*) ;;
    *) link_destinations="${link_destinations}${link_destinations:+${newline}}${dest}" ;;
  esac
}

discover_skill_names() {
  for skill_dir in "${repo}/skills"/*; do
    [ -d "${skill_dir}" ] || continue
    [ -f "${skill_dir}/SKILL.md" ] || continue
    basename -- "${skill_dir}"
  done | sort
}

codex_skills_dir() {
  codex_home=${CODEX_HOME:-"${HOME}/.codex"}
  printf '%s/skills\n' "${codex_home}"
}

claude_skills_dir() {
  claude_home=${CLAUDE_CONFIG_DIR:-"${HOME}/.claude"}
  printf '%s/skills\n' "${claude_home}"
}

opencode_skills_dir() {
  config_home=${XDG_CONFIG_HOME:-"${HOME}/.config"}
  printf '%s/opencode/skills\n' "${config_home}"
}

openclaw_skills_dir() {
  if [ -d "${HOME}/.openclaw" ]; then
    printf '%s/.openclaw/skills\n' "${HOME}"
  elif [ -d "${HOME}/.clawdbot" ]; then
    printf '%s/.clawdbot/skills\n' "${HOME}"
  elif [ -d "${HOME}/.moltbot" ]; then
    printf '%s/.moltbot/skills\n' "${HOME}"
  else
    printf '%s/.openclaw/skills\n' "${HOME}"
  fi
}

copilot_skills_dir() {
  printf '%s/.copilot/skills\n' "${HOME}"
}

gemini_skills_dir() {
  printf '%s/.gemini/skills\n' "${HOME}"
}

copy_dir() {
  source=${1}
  target=${2}
  target_parent=$(parent_dir "${target}")
  rm -rf "${target}"
  mkdir -p "${target_parent}"
  cp -R "${source}" "${target}"
}

install_canonical_skill() {
  source=${1}
  skill_name=$(basename -- "${source}")
  target="${canonical_root}/${skill_name}"

  if [ "${apply}" != "true" ]; then
    echo "would ${mode} ${source} -> ${target}"
    return 0
  fi

  mkdir -p "${canonical_root}"
  rm -rf "${target}"

  if [ "${mode}" = "symlink" ]; then
    ln -s "${source}" "${target}"
    echo "symlinked ${source} -> ${target}"
  else
    copy_dir "${source}" "${target}"
    mkdir -p "${target}/config"
    printf '%s\n' "${repo}" > "${target}/config/template_repo_path.txt"
    echo "copied ${source} -> ${target}"
  fi
}

link_skill() {
  skill_name=${1}
  dest_root=${2}
  source="${canonical_root}/${skill_name}"
  target="${dest_root}/${skill_name}"

  if [ "${apply}" != "true" ]; then
    echo "would symlink ${source} -> ${target}"
    return 0
  fi

  mkdir -p "${dest_root}"
  rm -rf "${target}"
  ln -s "${source}" "${target}"
  echo "symlinked ${source} -> ${target}"
}

uninstall_skill() {
  skill_name=${1}
  dest_root=${2}
  target="${dest_root}/${skill_name}"

  if [ "${apply}" != "true" ]; then
    echo "would remove ${target}"
    return 0
  fi

  rm -rf "${target}"
  echo "removed ${target}"
}

repo=$(find_repo)
canonical_root="${HOME}/.agents/skills"
link_destinations=""
remove_canonical="false"
skill_names=$(discover_skill_names)

if [ -z "${skill_names}" ]; then
  echo "No skills found under ${repo}/skills" >&2
  exit 1
fi

case " ${agents} " in
  *" all "*)
    agents="openai codex claude opencode copilot gemini openclaw"
    ;;
  *)
    ;;
esac

for agent in ${agents}; do
  case "${agent}" in
    openai|codex)
      agent_dest=$(codex_skills_dir)
      add_dest "${agent_dest}"
      remove_canonical="true"
      ;;
    claude|claude-code)
      agent_dest=$(claude_skills_dir)
      add_dest "${agent_dest}"
      ;;
    opencode)
      agent_dest=$(opencode_skills_dir)
      add_dest "${agent_dest}"
      ;;
    copilot|github-copilot)
      agent_dest=$(copilot_skills_dir)
      add_dest "${agent_dest}"
      ;;
    gemini)
      agent_dest=$(gemini_skills_dir)
      add_dest "${agent_dest}"
      ;;
    openclaw)
      agent_dest=$(openclaw_skills_dir)
      add_dest "${agent_dest}"
      ;;
    *)
      echo "skip ${agent}: unknown agent"
      ;;
  esac
done

for skill_name in ${skill_names}; do
  source="${repo}/skills/${skill_name}"
  if [ "${action}" = "uninstall" ]; then
    printf '%s\n' "${link_destinations}" | while IFS= read -r dest_root; do
      [ -n "${dest_root}" ] || continue
      uninstall_skill "${skill_name}" "${dest_root}"
    done
    if [ "${remove_canonical}" = "true" ]; then
      uninstall_skill "${skill_name}" "${canonical_root}"
    fi
    continue
  fi

  install_canonical_skill "${source}"
  printf '%s\n' "${link_destinations}" | while IFS= read -r dest_root; do
    [ -n "${dest_root}" ] || continue
    link_skill "${skill_name}" "${dest_root}"
  done
done

printf '%s\n' "${link_destinations}" | while IFS= read -r dest_root; do
  [ -n "${dest_root}" ] || continue
  uninstall_skill "install-agents-file-template-skills" "${dest_root}"
done

if [ "${remove_canonical}" = "true" ]; then
  uninstall_skill "install-agents-file-template-skills" "${canonical_root}"
fi

if [ "${apply}" != "true" ]; then
  echo "Dry run only. Re-run with --apply to ${action}."
fi
