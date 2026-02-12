# .PHONY: requirements requirements-prod requirements-dev setup run test demo downcerts clean-certs
.PHONY: requirements requirements-prod requirements-dev setup run test demo downcerts clean-certs

CERTS_DIR = certs
PRIVATE_KEY = $(CERTS_DIR)/jwt-private.pem
PUBLIC_KEY = $(CERTS_DIR)/jwt-public.pem

certs:
	@echo "Generating JWT RSA keys..."
	@mkdir -p $(CERTS_DIR)
	@openssl genrsa -out $(PRIVATE_KEY) 2048
	@openssl rsa -in $(PRIVATE_KEY) -outform PEM -pubout -out $(PUBLIC_KEY)
	@chmod 600 $(PRIVATE_KEY)
	@chmod 644 $(PUBLIC_KEY)
	@echo "Keys generated in $(CERTS_DIR)/"

	
requirements: requirements-prod requirements-dev
	@echo "✅ All requirements files updated!"

requirements-prod:
	uv pip compile pyproject.toml -o requirements.txt
	@echo "✅ Production requirements generated"

requirements-dev:
	uv pip compile pyproject.toml --extra dev -o requirements-dev.txt
	@echo "✅ Development requirements generated"

run:
	docker-compose up --build

test:
	pytest

demo:
	@echo "Starting demo environment..."
	docker-compose -f docker-compose.demo.yml up --build

down:
	docker-compose down

clean:
	@echo "Cleaning up..."
	docker-compose down -v
	rm -rf __pycache__
	rm -rf .pytest_cache
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true