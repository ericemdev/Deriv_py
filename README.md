# Deriv API Python Implementation

This project provides a Python-based implementation for interacting with the Binary.com Deriv API. It includes functionalities such as connecting to the WebSocket, executing trades, fetching balance and available symbols, and more.

## API Token and App ID

Before using the Deriv API, you need to obtain two important credentials:
- **API Token**: This token authenticates your requests to the API.
- **App ID**: This identifies your app in the Deriv ecosystem.

### Steps to Obtain API Token and App ID:

#### 1. **API Token**:
- Go to the [Deriv API Token Management](https://app.deriv.com/account/api-token) page.
- Log in with your Deriv account.
- Generate a new API token. You can choose between a demo token (for testing purposes) and a real token (for live trading).
- **Important**: Once generated, make sure to copy the API token as it will not be shown again.

#### 2. **App ID**:
- Go to the [Deriv Developer Documentation](https://developers.deriv.com/docs/introduction) page to create an App ID. This ID is required for connecting your script to the API.

## Installation

1. **Clone the repository**:

```bash

git clone https://github.com/ericemdev/derivPy.git
```
2. **Navigate to the project directory**:

```bash

cd derivPy
```
3. **Create a virtual environment**:

```bash

python3 -m venv venv
```
4. **Create a `.env` file and add the API credentials**:

```bash

touch .env
```
The `.env` file should contain the following variables:

```bash

DERIV_APP_ID=your_app_id
DERIV_API_TOKEN=your_api_token
WS_URL=your_websocket_url
```
use the token and app id you generated from the steps above

5. **Install the dependencies**:

```bash

pip install -r requirements.txt
```
   

## Example Commands

### Fetching Available Symbols
``edit the line in test.py to fetch the available symbols``
```python

  "data": base64.b64encode(b"SYMBOLS").decode()  # fetch symbols
   
```
in your terminal run the following command to fetch the available symbols
```bash
  
python test.py
```   
you should see the list of symbols example :
```bash

{
    "symbols": [
        "frxEURUSD"
    ]
}
```   
you can specify the symble of what you want eg binary , forex etc

```python

  "data": base64.b64encode(b"SYMBOLS:binary").decode()  # fetch binary symbols
```


### Fetching Balance
``edit the line in test.py to fetch the balance``
```python

  "data": base64.b64encode(b"BALANCE").decode(),  # fetch balance 
```
in your terminal run the following command to fetch the available symbols
```bash

python test.py
```
you should see the available balance example output
```bash

{
    "balance": 10000
}
```

### Placing a Trade
``edit the line in test.py to place a trade``
```python

  "data": base64.b64encode(b"buy frxAUDUSD Q=10 E=15m").decode() # place a trade

```
the commands are explained below
```bash
- symbol: The trading symbol (e.g., frxAUDUSD).
- stake: The amount to stake.
- duration: The duration of the trade, followed by the unit (m for minutes, h for hours, d for days).
- sl: Stop Loss value.
- tp: Take Profit value.
```
### Closing a Trade

in your terminal run the following command to place a trade
```bash

python test.py
```

you should see the trade details example output
```bash

Executing BUY command for symbol: FRXAUDUSD
Sending trade request: {'buy': 1, 'price': 10.0, 'parameters': {'symbol': 'FRXAUDUSD', 'basis': 'stake', 'duration': 1, 'duration_unit': 'd', 'contract_type': 'CALL', 'currency': 'USD', 'amount': 10.0}}
Trade response received:
{
    'balance_after': your balance after the trade,
    'buy_price': 10,
    'contract_id': 26671***3748,
    'longcode': 'Win payout if AUD/USD is strictly higher than entry spot at close on 2024-12-20.',
    'payout': 1266.64,
    'purchase_time': 1734599433,
    'shortcode': 'CALL_FRXAUDUSD_1266.64_1734599433_1734728100_S0P_0',
    'start_time': 1734599433,
    'transaction_id': 531717280588
}
Trade successfully executed with contract ID 266718143748. Your new balance is 3800 USD. 
Details:
- Symbol: FRXAUDUSD
- Amount: 10 USD
- Contract Type: CALL
- Duration: 1 day
- Payout: 1266.64 USD
- Expiry: 2024-12-20

```


###close a trade
``edit the line in test.py to close a trade``
```python

  "data": base64.b64encode(b"close frxAUDUSD stake=10").decode() # close a trade
```

in your terminal run the following command to close a trade
```bash

python test.py
```
you should see the trade details example output
```bash

Closing trade with contract ID 266718143748
Trade successfully closed. Your new balance is 3800 USD.
```
