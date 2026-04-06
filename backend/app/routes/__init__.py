from flask import Blueprint

bp_auth = Blueprint("auth", __name__, url_prefix="/api/v1/auth")
bp_users = Blueprint("users", __name__, url_prefix="/api/v1/users")
bp_products = Blueprint("products", __name__, url_prefix="/api/v1/products")
bp_cart = Blueprint("cart", __name__, url_prefix="/api/v1/cart")
bp_checkout = Blueprint("checkout", __name__, url_prefix="/api/v1/checkout")
bp_orders = Blueprint("orders", __name__, url_prefix="/api/v1/orders")
bp_payments = Blueprint("payments", __name__, url_prefix="/api/v1/payments")
bp_admin = Blueprint("admin", __name__, url_prefix="/api/v1/admin")
bp_debug = Blueprint("debug", __name__, url_prefix="/api/v1/debug")
bp_misc = Blueprint("misc", __name__, url_prefix="/api/v1")

# Import side effects: attach view functions to blueprints
from app.routes import auth as _auth  # noqa: E402, F401
from app.routes import users as _users  # noqa: E402, F401
from app.routes import products as _products  # noqa: E402, F401
from app.routes import cart as _cart  # noqa: E402, F401
from app.routes import checkout as _checkout  # noqa: E402, F401
from app.routes import orders as _orders  # noqa: E402, F401
from app.routes import payments as _payments  # noqa: E402, F401
from app.routes import admin as _admin  # noqa: E402, F401
from app.routes import debug as _debug  # noqa: E402, F401
from app.routes import misc as _misc  # noqa: E402, F401
