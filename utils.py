import firebase_admin
from firebase_admin import firestore
firebase_admin.initialize_app()


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
            params[param] = value

    # Infer 'symbol' from the remaining message if not explicitly provided
    if "symbol" in values and "symbol" not in params:
        words = message.split()
        if len(words) > 1:
            params["symbol"] = words[1]

    # Translate 'q' to 'stake'
    if "quantity" in params:
        params["stake"] = float(params.pop("quantity"))
    # sl and tp converted to float
    if "sl" in params:
        params["sl"] = float(params["sl"])
    if "tp" in params:
        params["tp"] = float(params["tp"])
    # Translate 'expiry' to 'duration'
    if "expiry" in params:
        params["duration"] = params.pop("expiry")

    print(f"Extracted Params: {params}")  # Debug log
    return [params, message]


def format(value, options={"BUY": ["LONG", "1"], "SELL": ["SHORT", "-1"], "CLOSE": ["0", "FLAT"], "CANCEL": ["EXIT"], "BALANCE": ["BAL", "FUNDS"], "SYMBOLS": ["SYM", "ASSETS"]}):
    if value in options:
        return value

    formatted = None
    for map in options:
        if value in options[map]:
            formatted = map

    print(f"Formatted Value: {formatted}")  # Debug log
    return formatted


def saveLog(message):
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




def format(value, options={"BUY": ["LONG", "1"], "SELL": ["SHORT", "-1"], "CLOSE": ["0", "FLAT"], "CANCEL": ["EXIT"], "BALANCE": ["BAL", "FUNDS"], "SYMBOLS": ["SYM", "ASSETS"]}):

    if value in options:
        return value

    formatted = None
    for map in options:
        if value in options[map]:
            formatted = map

    return formatted


def saveLog (message):

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