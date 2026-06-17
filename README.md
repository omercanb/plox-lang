# Board Game Stock Exchange
A web app that simulates a stock exchange for board games where users buy and sell board games off of the app. \
Just a fun way to test out what a stock exchange behaves as and board games are only used in name. \
Also has a programming language built into it based on https://craftinginterpreters.com/ that acts as an interface to the exchange. 

# Running the program
Install dependencies
```bash
pip install -e .
```
```bash
pip install -e ./lang
```
Initialize the db and seed
```bash
flask --app d20 init-db && flask --app d20 seed
```
Run
```bash
flask --app d20 run --debug
```

Log in \
Username: user1 \
Password: pass

# Stack
Flask
HTMX
Bootstrap
