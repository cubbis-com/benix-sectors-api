"""
Trader & Market Analyst AI Agent.
Calculates technical, fundamental, bandarmology, and foreign flow signals.
"""
from typing import Dict, Any, List

class TraderAnalystAgent:
    """Specialized Analyst Agent for evaluating trade setups, valuations, and broker flows."""

    @staticmethod
    def analyze_stock(symbol: str, stock_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Synthesizes raw data from Sectors API into high-value trader insights:
        - Valuation assessment (P/E, Dividend Yield, Market Cap)
        - Bandarmology & smart money concentration
        - Foreign flow trajectory
        - Key price levels (Support & Resistance)
        - Sentiment bias (BULLISH, BEARISH, NEUTRAL)
        """
        report = stock_data.get("report", {})
        overview = report.get("overview", {})
        valuation = report.get("valuation", {})
        dividend = report.get("dividend", {})
        foreign_flow = stock_data.get("foreign_flow", [])
        top_brokers = stock_data.get("top_brokers", {})

        last_price = overview.get("last_close_price") or 0
        market_cap = overview.get("market_cap") or 0
        company_name = report.get("company_name") or symbol

        # 1. Valuation analysis
        # Check P/E if available
        pe_ratio = valuation.get("pe_ttm") or valuation.get("forward_pe")
        dividend_yield = dividend.get("total_yield") or overview.get("yield_ttm") or 0.0

        val_status = "FAIR_VALUE"
        if pe_ratio and isinstance(pe_ratio, (int, float)):
            if pe_ratio < 12:
                val_status = "UNDERVALUED"
            elif pe_ratio > 25:
                val_status = "EXPENSIVE"

        # 2. Foreign Flow analysis
        foreign_net_total = 0
        if isinstance(foreign_flow, list) and foreign_flow:
            for item in foreign_flow[-5:]:  # Last 5 records
                net = item.get("net_foreign_inflow") or 0
                if isinstance(net, (int, float)):
                    foreign_net_total += net

        if foreign_net_total > 50_000_000_000:  # > 50 Miliar
            foreign_status = "STRONG_ACCUMULATION"
        elif foreign_net_total < -50_000_000_000:
            foreign_status = "HEAVY_DISTRIBUTION"
        else:
            foreign_status = "NEUTRAL_FLOW"

        # 3. Bandarmology / Broker concentration
        top_buyers = top_brokers.get("top_buyers", []) if isinstance(top_brokers, dict) else []
        top_sellers = top_brokers.get("top_sellers", []) if isinstance(top_brokers, dict) else []

        bandar_status = "BALANCED"
        if len(top_buyers) > 0 and len(top_sellers) > 0:
            buy_val = sum(b.get("net_buy_value", 0) for b in top_buyers[:3] if isinstance(b.get("net_buy_value"), (int, float)))
            sell_val = abs(sum(s.get("net_sell_value", 0) for s in top_sellers[:3] if isinstance(s.get("net_sell_value"), (int, float))))
            if buy_val > sell_val * 1.3:
                bandar_status = "BIG_ACCUMULATION"
            elif sell_val > buy_val * 1.3:
                bandar_status = "BIG_DISTRIBUTION"

        # 4. Overall Trading Bias
        score = 0
        if val_status == "UNDERVALUED": score += 1
        if foreign_status == "STRONG_ACCUMULATION": score += 2
        elif foreign_status == "HEAVY_DISTRIBUTION": score -= 2
        if bandar_status == "BIG_ACCUMULATION": score += 2
        elif bandar_status == "BIG_DISTRIBUTION": score -= 2

        if score >= 2:
            bias = "BULLISH"
        elif score <= -2:
            bias = "BEARISH"
        else:
            bias = "NEUTRAL"

        # 5. Pivot price levels (Support & Resistance)
        if last_price and isinstance(last_price, (int, float)) and last_price > 0:
            s1 = round(last_price * 0.97)
            s2 = round(last_price * 0.94)
            r1 = round(last_price * 1.03)
            tp = round(last_price * 1.08)
        else:
            s1, s2, r1, tp = None, None, None, None

        return {
            "symbol": symbol,
            "company_name": company_name,
            "last_price": last_price,
            "market_cap": market_cap,
            "bias": bias,
            "valuation_status": val_status,
            "pe_ratio": pe_ratio,
            "dividend_yield_pct": round(dividend_yield * 100, 2) if isinstance(dividend_yield, (int, float)) else 0,
            "foreign_flow_status": foreign_status,
            "foreign_flow_net_idr": foreign_net_total,
            "bandarmology_status": bandar_status,
            "key_levels": {
                "support_1": s1,
                "support_2": s2,
                "resistance_1": r1,
                "target_price": tp
            },
            "top_accumulating_brokers": [b.get("broker_code") for b in top_buyers[:3]] if top_buyers else [],
            "top_distributing_brokers": [s.get("broker_code") for s in top_sellers[:3]] if top_sellers else []
        }

    @staticmethod
    def _extract_list(raw_data: Any, key_name: str = None) -> List[Dict[str, Any]]:
        if not raw_data:
            return []
        if isinstance(raw_data, list):
            return raw_data
        if isinstance(raw_data, dict):
            if key_name and key_name in raw_data:
                sub = raw_data[key_name]
                if isinstance(sub, dict):
                    # e.g. {'1d': [...]}
                    for k in ["1d", "7d", "14d", "30d", "365d"]:
                        if k in sub and isinstance(sub[k], list):
                            return sub[k]
                    return list(sub.values())[0] if sub else []
                if isinstance(sub, list):
                    return sub
            # Date-keyed dictionary like most-traded: {'2026-10-05': [...]}
            sorted_keys = sorted(raw_data.keys(), reverse=True)
            if sorted_keys and isinstance(raw_data[sorted_keys[0]], list):
                return raw_data[sorted_keys[0]]
            # Fallback to first value
            for v in raw_data.values():
                if isinstance(v, list):
                    return v
        return []

    @classmethod
    def analyze_market_overview(cls, pulse_data: Dict[str, Any]) -> Dict[str, Any]:
        """Synthesizes market pulse into broader market regime insight."""
        gainers = cls._extract_list(pulse_data.get("top_gainers"), "top_gainers")
        losers = cls._extract_list(pulse_data.get("top_losers"), "top_losers")
        traded = cls._extract_list(pulse_data.get("most_traded"))

        sentiment = "NEUTRAL"
        if len(gainers) > len(losers):
            sentiment = "BULLISH_DOMINANT"
        elif len(losers) > len(gainers):
            sentiment = "BEARISH_CORRECTION"

        return {
            "market_sentiment": sentiment,
            "top_gainer_symbol": gainers[0].get("symbol") if gainers else None,
            "top_gainer_pct": gainers[0].get("price_change") if gainers else None,
            "top_volume_stock": traded[0].get("symbol") if traded else None,
            "active_stocks_count": len(gainers) + len(losers)
        }

trader_agent = TraderAnalystAgent()
