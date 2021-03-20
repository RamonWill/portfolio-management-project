import pandas as pd


class Reconciliation(object):
    def __init__(self, oanda_positions, prms_positions):
        self.oanda_positions = oanda_positions
        self.prms_positions = prms_positions

    def generate_rec(self):
        df_oanda = pd.DataFrame([vars(header) for header in self.oanda_positions])
        df_prms = pd.DataFrame([vars(header) for header in self.prms_positions])
        if df_oanda.empty:
            df_oanda = pd.DataFrame(
                columns=["name", "units", "avg_price", "unrel_pnl", "pnl"]
            )
        if df_prms.empty:
            df_prms = pd.DataFrame(columns=["name", "prms_units", "prms_avg_price"])
        rec = df_oanda.merge(df_prms, on="name", how="outer")
        rec["Position Diff"] = rec["units"] - rec["prms_units"]
        rec["Price Diff"] = rec["avg_price"] - rec["prms_avg_price"]
        commentary = []
        for row in rec.itertuples():
            position_diff = row[8]
            price_diff = row[9]

            if position_diff < 0.01 and price_diff < 0.01:
                commentary.append("OK")
            elif position_diff < 0.01 and price_diff > 0.01:
                commentary.append("Price Break")
            elif position_diff > 0.01 and price_diff < 0.01:
                commentary.append("Position Break")
            else:
                commentary.append("Position and Price Break")

        rec["Commentary"] = commentary
        return rec

    def num_matches(self):
        rec = self.generate_rec()
        if rec is None:
            return "There are no positions"
        total_records = len(rec)
        matches = len(rec.query("Commentary == 'OK'"))
        breaks = total_records - matches

        if total_records == matches:
            return "There are no position breaks"
        else:
            return f"{breaks} out of {total_records}\npositions have breaks"
