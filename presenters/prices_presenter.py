class PricesPresenter(object):
    def __init__(self, view, alpha_vantage):
        self.view = view
        self._alpha_vantage = alpha_vantage

    def create_chart(self, period, indicator, currency1, currency2):
        if indicator == "No Indicator":
            chart_data = self._alpha_vantage.get_fx_prices(
                intervals=period, from_symbol=currency1, to_symbol=currency2
            )
        else:
            chart_data = self._alpha_vantage.get_fx_prices_with_techincal(
                intervals=period,
                from_symbol=currency1,
                to_symbol=currency2,
                technical_indicator=indicator,
            )
        self.view.display_prices(chart_data)
        self.view.draw_chart(indicator=indicator)
