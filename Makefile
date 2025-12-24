db:
	@chroma run --host localhost --port 1989 --path .\apps\database\data\
backend:
	@cd apps/backend && uv run api.py
frontend:
	@cd apps/frontend && uv run streamlit run app.py --server.port 2001 --server.address localhost
all: db backend frontend

docker:
	@docker-compose up --build