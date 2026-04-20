from time import sleep

import flask
from flask import g, render_template, request

from d20.db.market.test import get_counts, increment_count

from . import bp, market_login_required


@bp.route("/test/<int:counter_id>")
@market_login_required
def test(counter_id):
    owner_id = g.market_participant["id"]
    counts = get_counts(owner_id, counter_id)
    increment_count(owner_id, counter_id)
    return render_template("market/test.html", counts=counts, counter_id=counter_id)


@bp.route("/test/<int:counter_id>/stream")
@market_login_required
def test_stream(counter_id):
    lines = ["YO was good", "my gang", "i hope the day is good"]

    def stream():
        for line in lines:
            sleep(0.5)
            print(f"event: output\ndata: {line}\n\n")
            yield f"event: output\ndata: {line}\n\n"
        print("event: done\ndata:\n\n")
        yield "event: done\ndata:\n\n"

    resp = flask.Response(stream(), mimetype="text/event-stream")
    # We may need these later if deploying
    # resp.headers["Cache-Control"] = "no-cache"
    # resp.headers["X-Accel-Buffering"] = "no"
    return resp


@bp.route("/test/running_button")
@market_login_required
def running_button():
    return render_template("market/htmx/_running_button.html")


@bp.route("/test/run_button")
@market_login_required
def run_button():
    counter_id = request.args.get("counter_id")
    return render_template("market/htmx/_run_button.html", counter_id=counter_id)


@bp.route("/test/running_container")
@market_login_required
def running_container():
    counter_id = request.args.get("counter_id")
    return render_template("market/htmx/_running_container.html", counter_id=counter_id)
