.PHONY: start-postgres
start-postgres:
	@docker compose -f docker/docker-compose-postgres.yml up -d

.PHONY: stop-postgres
stop-postgres:
	@docker compose -f docker/docker-compose-postgres.yml down

.PHONY: bump-patch
bump-patch:
	@bump2version patch
	@git push --tags
	@git push

.PHONY: bump-minor
bump-minor:
	@bump2version minor
	@git push --tags
	@git push

.PHONY: bump-major
bump-major:
	@bump2version major
	@git push --tags
	@git push

.PHONY: build-test
build-test:
	@docker compose -f docker/docker-compose-test.yml build

.PHONY: test
test:
	@docker compose -f docker/docker-compose-test.yml down
	@docker compose -f docker/docker-compose-test.yml up --exit-code-from common_modules_test_runner
