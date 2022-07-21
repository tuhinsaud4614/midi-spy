Setup virtual environment

```sh
python3 -m venv .venv
source .venv/bin/activate
```

Generate requirements.txt

```sh
pip freeze > requirements.txt
```

Install package from requirements.txt

```sh
pip install -r requirements.txt
```

Initial prisma schema from sqlite

```sh
prisma init --datasource-provider sqlite
```

Migrate DB for prisma
```sh
prisma migrate [db_Name] --name initialize
```

Push DB for prisma
```sh
prisma db push
```

Generate prisma client
```sh
prisma generate
```

Run fast api server
```sh
uvicorn main:app --reload
```
