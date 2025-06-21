from flask import Flask, request, jsonify, session
from flask_swagger_ui import get_swaggerui_blueprint
from flask_cors import CORS
from kite_trade import KiteApp, get_enctoken
import json
import os
from datetime import timedelta

app = Flask(__name__)
app.secret_key = os.urandom(24)  # Required for session
app.permanent_session_lifetime = timedelta(days=1)  # Session expires after 1 day

# Enable CORS
CORS(app, 
     supports_credentials=True,
     origins=["*"],
     methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
     allow_headers=["Content-Type", "Authorization", "X-Enctoken"])

# Swagger configuration
SWAGGER_URL = '/swagger'
API_URL = '/swagger.json'

swaggerui_blueprint = get_swaggerui_blueprint(
    SWAGGER_URL,
    API_URL,
    config={
        'app_name': "Kite Trading API"
    }
)

app.register_blueprint(swaggerui_blueprint, url_prefix=SWAGGER_URL)

@app.route('/swagger.json')
def swagger_json():
    with open('swagger.json', 'r') as f:
        return f.read(), 200, {'Content-Type': 'application/json'}

# Create Swagger JSON
swagger_config = {
    "swagger": "2.0",
    "info": {
        "title": "Kite Trading API",
        "description": "API for Zerodha Kite trading operations",
        "version": "1.0.0"
    },
    "basePath": "/",
    "schemes": ["https"],
    "securityDefinitions": {
        "ApiKeyAuth": {
            "type": "apiKey",
            "in": "header",
            "name": "X-Enctoken"
        }
    },
    "paths": {
        "/login": {
            "post": {
                "summary": "Login to Kite",
                "parameters": [
                    {
                        "name": "body",
                        "in": "body",
                        "required": True,
                        "schema": {
                            "type": "object",
                            "properties": {
                                "userid": {"type": "string"},
                                "password": {"type": "string"},
                                "twofa": {"type": "string"}
                            }
                        }
                    }
                ],
                "responses": {
                    "200": {
                        "description": "Login successful"
                    }
                }
            }
        },
        "/instruments": {
            "get": {
                "summary": "Get instruments",
                "security": [{"ApiKeyAuth": []}],
                "parameters": [
                    {
                        "name": "exchange",
                        "in": "query",
                        "type": "string",
                        "required": False
                    }
                ],
                "responses": {
                    "200": {
                        "description": "List of instruments"
                    }
                }
            }
        },
       
        "/historical-data": {
            "get": {
                "summary": "Get historical data",
                "security": [{"ApiKeyAuth": []}],
                "parameters": [
                    {
                        "name": "instrument_token",
                        "in": "query",
                        "type": "integer",
                        "required": True
                    },
                    {
                        "name": "from_date",
                        "in": "query",
                        "type": "string",
                        "required": True
                    },
                    {
                        "name": "to_date",
                        "in": "query",
                        "type": "string",
                        "required": True
                    },
                    {
                        "name": "interval",
                        "in": "query",
                        "type": "string",
                        "required": True
                    }
                ],
                "responses": {
                    "200": {
                        "description": "Historical data"
                    }
                }
            }
        },
        "/place-order": {
            "post": {
                "summary": "Place a new order",
                "security": [{"ApiKeyAuth": []}],
                "parameters": [
                    {
                        "name": "body",
                        "in": "body",
                        "required": True,
                        "schema": {
                            "type": "object",
                            "properties": {
                                "variety": {"type": "string"},
                                "exchange": {"type": "string"},
                                "tradingsymbol": {"type": "string"},
                                "transaction_type": {"type": "string"},
                                "quantity": {"type": "integer"},
                                "product": {"type": "string"},
                                "order_type": {"type": "string"},
                                "price": {"type": "number"},
                                "validity": {"type": "string"},
                                "disclosed_quantity": {"type": "integer"},
                                "trigger_price": {"type": "number"},
                                "squareoff": {"type": "number"},
                                "stoploss": {"type": "number"},
                                "trailing_stoploss": {"type": "number"},
                                "tag": {"type": "string"}
                            }
                        }
                    }
                ],
                "responses": {
                    "200": {
                        "description": "Order placed successfully"
                    }
                }
            }
        },
        "/orders": {
            "get": {
                "summary": "Get all orders",
                "security": [{"ApiKeyAuth": []}],
                "responses": {
                    "200": {
                        "description": "List of all orders"
                    }
                }
            }
        },
        "/holdings": {
            "get": {
                "summary": "Get holdings",
                "security": [{"ApiKeyAuth": []}],
                "responses": {
                    "200": {
                        "description": "List of holdings"
                    }
                }
            }
        },
        "/positions": {
            "get": {
                "summary": "Get positions",
                "security": [{"ApiKeyAuth": []}],
                "responses": {
                    "200": {
                        "description": "List of positions"
                    }
                }
            }
        },
        "/profile": {
            "get": {
                "summary": "Get user profile",
                "security": [{"ApiKeyAuth": []}],
                "responses": {
                    "200": {
                        "description": "User profile information"
                    }
                }
            }
        },
        "/margins": {
            "get": {
                "summary": "Get user margins",
                "security": [{"ApiKeyAuth": []}],
                "responses": {
                    "200": {
                        "description": "User margin information"
                    }
                }
            }
        },
        "/modify-order": {
            "put": {
                "summary": "Modify an existing order",
                "security": [{"ApiKeyAuth": []}],
                "parameters": [
                    {
                        "name": "body",
                        "in": "body",
                        "required": True,
                        "schema": {
                            "type": "object",
                            "properties": {
                                "variety": {"type": "string"},
                                "order_id": {"type": "string"},
                                "parent_order_id": {"type": "string"},
                                "quantity": {"type": "integer"},
                                "price": {"type": "number"},
                                "order_type": {"type": "string"},
                                "trigger_price": {"type": "number"},
                                "validity": {"type": "string"},
                                "disclosed_quantity": {"type": "integer"}
                            }
                        }
                    }
                ],
                "responses": {
                    "200": {
                        "description": "Order modified successfully"
                    }
                }
            }
        },
        "/cancel-order": {
            "delete": {
                "summary": "Cancel an existing order",
                "security": [{"ApiKeyAuth": []}],
                "parameters": [
                    {
                        "name": "body",
                        "in": "body",
                        "required": True,
                        "schema": {
                            "type": "object",
                            "properties": {
                                "variety": {"type": "string"},
                                "order_id": {"type": "string"},
                                "parent_order_id": {"type": "string"}
                            }
                        }
                    }
                ],
                "responses": {
                    "200": {
                        "description": "Order cancelled successfully"
                    }
                }
            }
        }
    }
}

# Save Swagger configuration
with open('swagger.json', 'w') as f:
    json.dump(swagger_config, f)

def get_kite_instance():
    # First try to get enctoken from session
    enctoken = session.get('enctoken')
    # If not in session, try to get from header
    if not enctoken:
        enctoken = request.headers.get('X-Enctoken')
        if enctoken:
            # Store in session for future requests
            session['enctoken'] = enctoken
            session.permanent = True
    if not enctoken:
        return None
    return KiteApp(enctoken)

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    try:
        enctoken = get_enctoken(data['userid'], data['password'], data['twofa'])
        # Store enctoken in session
        session['enctoken'] = enctoken
        session.permanent = True  # Make session persistent
        return jsonify({
            "status": "success", 
            "message": "Login successful",
            "enctoken": enctoken
        })
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 400

@app.route('/instruments', methods=['GET'])
def get_instruments():
    kite = get_kite_instance()
    if not kite:
        return jsonify({"status": "error", "message": "Missing or invalid enctoken"}), 401
    
    exchange = request.args.get('exchange')
    try:
        instruments = kite.instruments(exchange)
        return jsonify({"status": "success", "data": instruments})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 400


@app.route('/historical-data', methods=['GET'])
def get_historical_data():
    kite = get_kite_instance()
    if not kite:
        return jsonify({"status": "error", "message": "Missing or invalid enctoken"}), 401
    
    try:
        instrument_token = int(request.args.get('instrument_token'))
        from_date = request.args.get('from_date')
        to_date = request.args.get('to_date')
        interval = request.args.get('interval')
        
        historical_data = kite.historical_data_v2(
            instrument_token=instrument_token,
            from_date=from_date,
            to_date=to_date,
            interval=interval
        )
        return jsonify({"status": "success", "data": historical_data})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 400

@app.route('/place-order', methods=['POST'])
def place_order():
    kite = get_kite_instance()
    if not kite:
        return jsonify({"status": "error", "message": "Missing or invalid enctoken"}), 401
    
    try:
        data = request.get_json()
        order_id = kite.place_order(**data)
        return jsonify({"status": "success", "order_id": order_id})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 400

@app.route('/orders', methods=['GET'])
def get_orders():
    kite = get_kite_instance()
    if not kite:
        return jsonify({"status": "error", "message": "Missing or invalid enctoken"}), 401
    
    try:
        orders = kite.orders()
        return jsonify({"status": "success", "data": orders})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 400

@app.route('/holdings', methods=['GET'])
def get_holdings():
    kite = get_kite_instance()
    if not kite:
        return jsonify({"status": "error", "message": "Missing or invalid enctoken"}), 401
    
    try:
        holdings = kite.holdings()
        return jsonify({"status": "success", "data": holdings})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 400

@app.route('/positions', methods=['GET'])
def get_positions():
    kite = get_kite_instance()
    if not kite:
        return jsonify({"status": "error", "message": "Missing or invalid enctoken"}), 401
    
    try:
        positions = kite.positions()
        return jsonify({"status": "success", "data": positions})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 400

@app.route('/profile', methods=['GET'])
def get_profile():
    kite = get_kite_instance()
    if not kite:
        return jsonify({"status": "error", "message": "Missing or invalid enctoken"}), 401
    
    try:
        profile = kite.profile()
        return jsonify({"status": "success", "data": profile})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 400
    
@app.route('/margins', methods=['GET'])
def get_margins():
    kite = get_kite_instance()
    if not kite:
        return jsonify({"status": "error", "message": "Missing or invalid enctoken"}), 401
    
    try:
        margins = kite.margins()
        return jsonify({"status": "success", "data": margins})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 400

@app.route('/modify-order', methods=['PUT'])
def modify_order():
    kite = get_kite_instance()
    if not kite:
        return jsonify({"status": "error", "message": "Missing or invalid enctoken"}), 401
    
    try:
        data = request.get_json()
        order_id = kite.modify_order(**data)
        return jsonify({"status": "success", "order_id": order_id})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 400

@app.route('/cancel-order', methods=['DELETE'])
def cancel_order():
    kite = get_kite_instance()
    if not kite:
        return jsonify({"status": "error", "message": "Missing or invalid enctoken"}), 401
    
    try:
        data = request.get_json()
        order_id = kite.cancel_order(**data)
        return jsonify({"status": "success", "order_id": order_id})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 400

@app.route('/', methods=['OPTIONS'])
@app.route('/<path:path>', methods=['OPTIONS'])
def handle_preflight(path=None):
    response = app.make_default_options_response()
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization, X-Enctoken'
    return response

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port) 