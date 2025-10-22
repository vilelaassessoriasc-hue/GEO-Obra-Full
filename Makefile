.PHONY: test-nodocker docker-check

docker-check:
    @bash scripts/check_docker.sh

test-nodocker:
    @bash scripts/codex_nodocker.sh