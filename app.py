from musicleague import app
from musicleague.environment import get_port
from musicleague.environment import is_debug


if __name__ == "__main__":
    debug = is_debug()
    port = get_port()
    app.run(host='0.0.0.0', port=port, debug=debug)
