from d20.db import get_db


def create_game(name, symbol):
    db = get_db()
    cursor = db.execute(
        "insert into Game (name, symbol) values (?, ?)",
        (name, symbol),
    )
    db.commit()
    return cursor.lastrowid


def get_games():
    return get_db().execute("select * from Game").fetchall()


def get_game(game_id):
    return get_db().execute("select * from Game where id = ?", (game_id,)).fetchone()


def get_game_by_name(name):
    return get_db().execute("select * from Game where name = ?", (name,)).fetchone()


def get_game_id_by_symbol(symbol):
    game = get_game_by_symbol(symbol)
    if not game:
        raise InvalidSymbolError(symbol)
    return game["id"]


class InvalidSymbolError(Exception):
    def __init__(self, symbol):
        self.symbol = symbol
        super().__init__(f"Symbol not found: {symbol}")


def get_game_by_symbol(symbol):
    return get_db().execute("select * from Game where symbol = ?", (symbol,)).fetchone()


def delete_game(game_id):
    db = get_db()
    db.execute("delete from Game where id = ?", (game_id,))
    db.commit()
