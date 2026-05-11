#!/bin/sh
set -eu

usage() {
  cat <<'USAGE'
Usage: install_agent_template_skills.sh [--repo PATH] [--agent NAME]... [--mode copy|symlink] [--apply] [--uninstall]

Agents:
  openai, codex   install to ${HOME}/.agents/skills
  claude          install to ${HOME}/.claude/skills
  opencode        install to ${HOME}/.claude/skills
  copilot         reports instruction-file guidance
  gemini          reports instruction-file guidance
  all             all known agents

Dry run is the default. Add --apply to install or uninstall.
USAGE
}

repo_arg="."
mode="copy"
apply="false"
action="install"
agents=""

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
  printf '%s\n' "  1) OpenAI/Codex (~/.agents/skills)"
  printf '%s\n' "  2) Claude Code (~/.claude/skills)"
  printf '%s\n' "  3) OpenCode (Claude-compatible ~/.claude/skills)"
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
      path=${1}
      ;;
    *)
      current_dir=$(pwd)
      path="${current_dir}/${1}"
      ;;
  esac
  if [ -d "${path}" ]; then
    cd -- "${path}" && pwd
  else
    path_parent=$(parent_dir "${path}")
    path_name=$(basename -- "${path}")
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

  echo "Could not find agents-file-templates. Run from the repo or set AGENTS_TEMPLATE_REPO." >&2
  exit 1
}

add_dest() {
  dest=${1}
  case " ${destinations} " in
    *" ${dest} "*) ;;
    *) destinations="${destinations}${destinations:+ }${dest}" ;;
  esac
}

copy_dir() {
  source=${1}
  target=${2}
  target_parent=$(parent_dir "${target}")
  rm -rf "${target}"
  mkdir -p "${target_parent}"
  cp -R "${source}" "${target}"
}

install_skill() {
  source=${1}
  dest_root=${2}
  target="${dest_root}/$(basename -- "${source}")"

  if [ "${apply}" != "true" ]; then
    echo "would ${mode} ${source} -> ${target}"
    return 0
  fi

  mkdir -p "${dest_root}"
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
destinations=""

case " ${agents} " in
  *" all "*)
    agents="openai codex claude opencode copilot gemini"
    ;;
  *)
    ;;
esac

for agent in ${agents}; do
  case "${agent}" in
    openai|codex)
      add_dest "${HOME}/.agents/skills"
      ;;
    claude|opencode)
      add_dest "${HOME}/.claude/skills"
      ;;
    copilot)
      echo "skip copilot: GitHub Copilot uses repository instruction files, not portable SKILL.md directories."
      ;;
    gemini)
      echo "skip gemini: Gemini commonly uses GEMINI.md context files; skill directory support depends on your CLI configuration."
      ;;
    *)
      echo "skip ${agent}: unknown agent"
      ;;
  esac
done

for dest_root in ${destinations}; do
  for skill_name in init-agents-file update-agents-file-templates; do
    source="${repo}/skills/${skill_name}"
    if [ "${action}" = "uninstall" ]; then
      uninstall_skill "${skill_name}" "${dest_root}"
      continue
    fi
    if [ ! -d "${source}" ]; then
      echo "skip missing skill: ${source}"
      continue
    fi
    install_skill "${source}" "${dest_root}"
  done
  uninstall_skill "install-agents-file-template-skills" "${dest_root}"
done

if [ "${apply}" != "true" ]; then
  echo "Dry run only. Re-run with --apply to ${action}."
fi
