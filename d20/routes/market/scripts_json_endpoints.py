import io
from contextlib import redirect_stderr, redirect_stdout

from flask import g, jsonify, render_template, request
from plox.runner import LoxRunner

from d20.db.game import InvalidSymbolError
from d20.db.market.orders import get_orders_by_script
from d20.db.market.participant_inventory import get_participant_inventory
from d20.db.market.trading_scripts import (
    create_script,
    delete_script,
    get_script,
    get_scripts_by_owner,
    update_script,
)
from d20.routes.market import market_api

from . import bp, market_login_required



@bp.route("/algorithmic/save_script", methods=("POST",))
@market_login_required
def save_script():
    participant_id = g.market_participant["id"]
    data = request.json
    code = data.get("code", "")
    update_script(participant_id, code)
    return jsonify({"success": True})
    



@bp.route("/algorithmic/load/orders/<int:script_id>", methods=("GET",))
@market_login_required
def algorithmic_load_orders(script_id):
    """Return the orders table component."""
    script = get_script(script_id)
    if not script or script["owner_id"] != g.market_participant["id"]:
        return "", 403

    orders = get_orders_by_script(script_id)
    return render_template("market/htmx/_orders_table_rows.html", orders=orders)


@bp.route("/algorithmic/scripts/orders/<int:script_id>", methods=("GET",))
@market_login_required
def get_script_orders(script_id):
    script = get_script(script_id)
    if not script:
        return jsonify({"success": False, "error": "Script not found"}), 404

    # Verify ownership
    if script["owner_id"] != g.market_participant["id"]:
        return jsonify({"success": False, "error": "Unauthorized"}), 403

    orders = get_orders_by_script(script_id)
    if orders:
        orders = [dict(order) for order in orders]
        return jsonify({"success": True, "data": orders})
    else:
        return jsonify({"success": False, "error": "An error occured."}), 500
