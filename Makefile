.PHONY: help install uninstall install-symlink validate

AGENTS ?= openai
MODE ?= copy

help:
	@printf '%s\n' 'Targets:'
	@printf '%s\n' '  make install          Install skills for AGENTS=openai by default'
	@printf '%s\n' '  make install-symlink  Install skills as symlinks'
	@printf '%s\n' '  make uninstall        Remove installed skills'
	@printf '%s\n' '  make validate         Run local validation checks'
	@printf '%s\n' ''
	@printf '%s\n' 'Examples:'
	@printf '%s\n' '  make install AGENTS="openai claude"'
	@printf '%s\n' '  make install-symlink AGENTS="openai claude opencode"'

install:
	@set -- $(AGENTS); \
	args=""; \
	for agent do args="$$args --agent $$agent"; done; \
	scripts/install_agent_template_skills.sh $$args --mode "$(MODE)" --apply

install-symlink:
	@$(MAKE) install MODE=symlink

uninstall:
	@set -- $(AGENTS); \
	args=""; \
	for agent do args="$$args --agent $$agent"; done; \
	scripts/install_agent_template_skills.sh $$args --uninstall --apply

validate:
	markdownlint --config "$${HOME}/.markdownlint.json" AGENTS.md README.md CHANGELOG.md TODO.md templates/**/*.md skills/**/*.md
	yamllint -c .yamllint templates.yml skills/*/agents/openai.yaml .yamllint
	python3 -m py_compile scripts/privacy_scan.py skills/init-agents-file/scripts/init_agents_file.py skills/update-agents-file-templates/scripts/update_agents_templates.py
	shellcheck --enable=all scripts/install_agent_template_skills.sh
	python3 scripts/privacy_scan.py .
