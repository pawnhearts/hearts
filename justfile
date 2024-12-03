set dotenv-load

migrate:
	beanie migrate -uri $MONGO_URI -db 'hearts' -p migrations/ --no-use-transaction

build:
	cd minihearts && npm run build && cp -r dist/* ../static/

serve:
	.venv/bin/uvicorn app:app --reload --host 0.0.0.0 --port 8080

watch:
    fswatch minihearts/src   | xargs -n1 -I{} just build
