SRC=src
STAGE?=local
LOGGING_CONFIG ?= logging.yaml

notlocal:
	@if [ $(STAGE) == 'local' ]; then echo "Set stage to dev or prod"; exit 1; fi

all: install test

env:
	STAGE="${STAGE}" \
	pipenv run python scripts/make_env.py > .env

install:
	pipenv --python 3.8.1 \
	&& pipenv lock --pre\
	&& pipenv install --dev \
	&& pipenv run pip install flake8 \
	&& yarn \
	&& pipenv run pre-commit install

install_test:
	pipenv --python 3.8.1 \
	&& pipenv install \
	&& pipenv run pip install flake8 \
	&& pipenv run pip install pytest \
	&& pipenv run pip install pytest-cov \
	&& pipenv run pip install pytest-mock \
	&& pipenv run pip install before_after \
	&& pipenv run pip install requests-mock \
	&& yarn

install_phase:
	pipenv --python 3.8.1 \
	&& pipenv install \
	&& yarn

lint:
	pipenv run flake8 $(SRC) $(MIGRATIONS)

format:
	pipenv run black $(SRC) $(MIGRATIONS)

test: env lint
	PYTHONPATH="$(SRC)" \
	pipenv run pytest -vvs \
		--cov=$(SRC) \
		--cov-report term-missing \
		--cov-fail-under 0

serve: env
	LOGGING_CONFIG=$(LOGGING_CONFIG) \
	pipenv run serverless wsgi serve --stage "$(STAGE)"

deploy: notlocal
	serverless deploy --stage "$(STAGE)" --verbose

package: notlocal
	serverless package --stage "$(STAGE)"

init: env
	PYTHONPATH="$(SRC)" \
	pipenv run flask db init

migrate: env
	PYTHONPATH="$(SRC)" \
	pipenv run flask db migrate

upgrade: env
	PYTHONPATH="$(SRC)" \
	pipenv run flask db upgrade

downgrade: env
	PYTHONPATH="$(SRC)" \
	pipenv run flask db downgrade

shell: env
	PYTHONPATH="$(SRC)" \
	pipenv run flask shell

sign-in: env
	PYTHONPATH="$(SRC)" \
	pipenv run flask cognito admin_initiate_auth ${EMAIL} ${PASSWORD}

sign-up: env
	PYTHONPATH="$(SRC)" \
	pipenv run flask cognito admin_create_user \
		${NAME} ${FAMILY_NAME} ${EMAIL} ${PHONE_NUMBER} ${TEMP_PASSWORD}

change-password: env
	PYTHONPATH="$(SRC)" \
	pipenv run flask cognito admin_change_password \
		${EMAIL} ${OLD_PASSWORD} ${NEW_PASSWORD}

clean:
	pipenv --rm \
	; rm -rf \
		.coverage \
		.pytest_cache \
		.serverless \
		build \
		dist \
		node_modules \
		yarn-error.log \
	; rm -rf `find . -type d -name ".cache"` \
	; rm -rf `find . -type f -name "*.py[co]"` \
	; rm -rf `find . -type d -name "*.egg-info"` \
	; rm -rf `find . -type d -name "pip-wheel-metadata"` \
	; rm -rf `find . -type d -name "__pycache__"` \
	; rm -rf `find . -type d -name "*.db"`
