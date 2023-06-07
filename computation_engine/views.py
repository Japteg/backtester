import copy
import pandas as pd

from rest_framework.views import APIView
from rest_framework.response import Response

from .constants import SHORT_STRADDLE_DEFAULT_PARAMS
from strategies.short_straddle.main import ShortStraddleManager


# Create your views here.
class ShortStraddle(APIView):

    def get(self, request):
        params = copy.copy(SHORT_STRADDLE_DEFAULT_PARAMS)
        # TODO: validate request first
        for key in request.GET:
            params[key] = request.GET[key]

        manager = ShortStraddleManager(**params)
        intraday_trade_log = manager.execute()
        intraday_trade_log.to_json()
        return Response(intraday_trade_log)
