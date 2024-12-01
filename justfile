set dotenv-load

migrate:
	beanie migrate -uri $MONGO_URI -db 'hearts' -p migrations/ --no-use-transaction

build:
	cd admin && npm run build && cp -r dist/* ../frontend/

serve:
	.venv/bin/uvicorn app:app --reload --host 0.0.0.0 --port 8080