# walleot/core.py
from paymcp import PayMCP, PaymentFlow, Mode

class Walleot:
    def __init__(self, mcp_instance, api_key=None, apiKey=None,  payment_flow: PaymentFlow = None, state_store = None,  mode: Mode = None):
        effective_api_key = api_key if api_key is not None else apiKey
        self._paymcp = PayMCP(
            mcp_instance,
            providers={"walleot": {"api_key": effective_api_key}},
            mode=mode,
            state_store=state_store,
            payment_flow=payment_flow
        )

    def __getattr__(self, item):
        return getattr(self._paymcp, item)
        

