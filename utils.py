import firebase_admin
from firebase_admin import firestore

# Initialize Firebase
firebase_admin.initialize_app()

# **Utility Functions**

def extract(values, data):

    def split_get(text, key):
        start = text.index(key) + len(key)
        portion = text[start:].strip()
        end = len(portion)
        try:
            end = portion.index(" ")
        except ValueError:
            pass
        return text[start:start + end]

    def parse_duration(duration):
        unit = duration[-1].lower()
        value = duration[:-1]
        if unit == 'm':
            return int(value), 'm'
        elif unit == 'h':
            return int(value), 'h'
        elif unit == 'd':
            return int(value), 'd'
        elif unit == 't':
            return int(value), 't'
        else:
            return int(value), 'm'

    params = {}
    message = data
    extracting = data.upper()

    for param in values:
        key = f" {param.upper()}="
        if key not in extracting and len(param) > 2:
            key = f" {param[:1].upper()}="

        if key in extracting:
            value = split_get(extracting, key)
            starting = extracting.index(key + value) + 1
            replace = message[starting:starting + len(key) + len(value)]
            message = message.replace(replace, '')
            extracting = extracting.replace(replace.upper(), '')
            if param == "expiry":
                duration_value, duration_unit = parse_duration(value)
                params["duration"] = duration_value
                params["duration_unit"] = duration_unit
            else:
                params[param] = value

    # Handle contract_id for CANCEL command
    if "contract_id" not in params and "CANCEL" in message.upper():
        words = message.split()
        for word in words:
            if word.isdigit():
                params["contract_id"] = word

    if "symbol" in values and "symbol" not in params:
        words = message.split()
        if len(words) > 1:
            params["symbol"] = words[1]

    if "quantity" in params:
        params["stake"] = float(params.pop("quantity"))
    if "sl" in params:
        params["sl"] = float(params["sl"])
    if "tp" in params:
        params["tp"] = float(params["tp"])

    print(f"Extracted Params: {params}")
    return [params, message]

def assign_defaults(params):
    """
    Assign default values for optional parameters.
    """
    params["quantity"] = params.get("quantity", "1")
    params["type"] = params.get("type", "Binary")
    params["expiry"] = params.get("expiry", "1")
    return params

def format(value, options={"BUY": ["LONG", "1"], "SELL": ["SHORT", "-1"], "CLOSE": ["0", "FLAT"], "CANCEL": ["EXIT"], "BALANCE": ["BAL", "FUNDS"], "SYMBOLS": ["SYM", "ASSETS"]}):
    """
    Format command or parameter based on pre-defined options.
    """
    if value in options:
        return value

    formatted = None
    for map in options:
        if value in options[map]:
            formatted = map

    print(f"Formatted Value: {formatted}")
    return formatted

def execute_trade(params):
    """
    Execute a trade based on extracted parameters.
    """
    symbol = params["symbol"]
    command = params["command"]
    quantity = params["quantity"]
    trade_type = params["type"]
    expiry = params["expiry"]

    if trade_type.lower() == "binary":
        # Logic for binary options trade
        print(f"Placing Binary Trade: {command} {symbol} Q={quantity} E={expiry}")
    elif trade_type.lower() == "digital":
        # Logic for digital options trade
        print(f"Placing Digital Trade: {command} {symbol} Q={quantity} E={expiry}")
    else:
        raise ValueError("Invalid trade type specified.")

def saveLog(message):
    """
    Save alert messages to Firebase Firestore.
    """
    print("Saving Log", message)
    return None

    FIELD_VALUE = firestore.firestore
    FIRESTORE = firestore.client()
    ALERTS = FIRESTORE.collection("alerts")
    ACTIVATIONS = FIRESTORE.collection("activations")

    batch = FIRESTORE.batch()
    alert = {
        "created": message["created"],
        "message": message["message"],
        "source": message["source"],
        "result": message["result"],
        "id": ALERTS.document().id,
        "activation": message["activation"]
    }
    if message["plan"] in ["1", "2"]:
        batch.set(ALERTS.document(alert["id"]), alert)

    batch.update(ACTIVATIONS.document(alert["activation"]), {
        "executed": FIELD_VALUE.SERVER_TIMESTAMP,
        "alerts": FIELD_VALUE.Increment(1),
        "daily.alerts": FIELD_VALUE.Increment(1),
        "meta.errors": FIELD_VALUE.Increment(1) if "FAILED" in alert["result"] else 0
    })

    try:
        batch.commit()
        print("Saved New Alert!", alert["id"])
    except e:
        print("Could not record alert", e)

    return None
