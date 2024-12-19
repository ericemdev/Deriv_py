from main import deriv
import base64

class AttrDict(dict):
    def __getattr__(self, item):
        return self[item]

def get_json():
    return {
        "method": "POST",
        "message": {
            "data": base64.b64encode(b"buy q=700 frxAUDUSD e=15m").decode(),  # Duration in minutes
            "attributes": {
                'platform': 'deriv',
                "activation": "S63D7RaUkghFBfZMdfJZ",
                "source": "test",
                "plan": "2"
            }
        }
    }

if __name__ == "__main__":
    req = AttrDict({"get_json": get_json})
    print(deriv(req.get_json()))
