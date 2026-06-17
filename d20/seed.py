import click

from d20.db.game import create_game
from d20.db.market.market_participant import (
    get_market_participant_by_customer,
    increment_available_cash,
)
from d20.db.market.orders import create_order
from d20.db.market.participant_inventory import increment_available_quantity
from d20.db.user import create_user


def seed_users():
    users = [("user1", "pass"), ("user2", "pass")]
    return [create_user(username, password) for username, password in users]


def seed_games():
    games = [
        ("Monopoly", "MNPLY"),
        ("Codenames", "CDNMS"),
        ("Catan", "CATAN"),
    ]
    return [create_game(name, symbol) for name, symbol in games]


def seed_orders(user_ids, game_ids):
    # Have user1 put out one buy and sell order for game 1 and 2
    user1 = user_ids[0]
    user1_market = get_market_participant_by_customer(user1)["id"]
    increment_available_cash(user1_market, 100)
    game1 = game_ids[0]
    create_order(user1_market, game1, "LIMIT", "BUY", 20, 2)
    game2 = game_ids[1]
    increment_available_quantity(user1_market, game2, 3)
    create_order(user1_market, game2, "LIMIT", "SELL", 30, 3)
    # Have user1 match the sell order to buy a game
    user2 = user_ids[1]
    user2_market = get_market_participant_by_customer(user2)["id"]
    increment_available_cash(user2_market, 100)
    create_order(user2_market, game2, "MARKET", "BUY", None, 1)


def seed_the_universe():
    user_ids = seed_users()
    game_ids = seed_games()
    seed_orders(user_ids, game_ids)


@click.command("seed")
def seed_db_command():
    seed_the_universe()
    click.echo("Seeded database.")
