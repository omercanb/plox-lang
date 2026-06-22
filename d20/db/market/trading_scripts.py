from d20.db import get_db


def create_script(owner_id, name, code):
    """Create a new trading script.
    
    Args:
        owner_id: MarketParticipant ID (owner of the script)
        name: Name of the script
        code: Script code
        
    Returns:
        The ID of the newly created script
    """
    db = get_db()
    cursor = db.execute(
        "insert into TradingScript (name, code, owner_id) values (?, ?, ?)",
        (name, code, owner_id),
    )
    db.commit()
    return cursor.lastrowid


def get_script(script_id):
    """Get a script by ID."""
    return (
        get_db()
        .execute("select * from TradingScript where id = ?", (script_id,))
        .fetchone()
    )

def update_script(participant_id, code):
    db = get_db()
    db.execute(
            "update MarketPariticipant set script_code = ? where id = ?",
            (code, participant_id)
            )
    db.commit()

def delete_script(script_id):
    """Delete a script by ID."""
    db = get_db()
    db.execute("delete from TradingScript where id = ?", (script_id,))
    db.commit()
