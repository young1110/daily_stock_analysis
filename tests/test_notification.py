# -*- coding: utf-8 -*-
"""
Tests for notification report: _has_meaningful_vol/chip and dashboard report content.
Cross-validates that 量能/筹码 blocks are omitted when data is N/A, and MACD/RSI + 解读 appear when present.
"""

import os
import sys
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.notification import NotificationService
from src.analyzer import AnalysisResult


class TestNotificationHelpers(unittest.TestCase):
    """Test _has_meaningful_vol and _has_meaningful_chip."""

    def test_has_meaningful_vol_false_when_empty(self):
        self.assertFalse(NotificationService._has_meaningful_vol(None))
        self.assertFalse(NotificationService._has_meaningful_vol({}))
        self.assertFalse(NotificationService._has_meaningful_vol({"volume_ratio": None, "turnover_rate": None}))
        self.assertFalse(NotificationService._has_meaningful_vol({"volume_ratio": "N/A", "turnover_rate": "N/A"}))
        self.assertFalse(NotificationService._has_meaningful_vol({"volume_ratio": "None", "turnover_rate": ""}))

    def test_has_meaningful_vol_true_when_any_value(self):
        self.assertTrue(NotificationService._has_meaningful_vol({"volume_ratio": 1.2, "turnover_rate": None}))
        self.assertTrue(NotificationService._has_meaningful_vol({"volume_ratio": None, "turnover_rate": 5.0}))
        self.assertTrue(NotificationService._has_meaningful_vol({"volume_ratio": "1.5", "turnover_rate": "N/A"}))

    def test_has_meaningful_chip_false_when_empty(self):
        self.assertFalse(NotificationService._has_meaningful_chip(None))
        self.assertFalse(NotificationService._has_meaningful_chip({}))
        self.assertFalse(
            NotificationService._has_meaningful_chip(
                {"profit_ratio": None, "avg_cost": None, "concentration": None}
            )
        )
        self.assertFalse(
            NotificationService._has_meaningful_chip(
                {"profit_ratio": "N/A", "avg_cost": "N/A", "concentration": "N/A"}
            )
        )

    def test_has_meaningful_chip_true_when_any_value(self):
        self.assertTrue(
            NotificationService._has_meaningful_chip({"profit_ratio": 0.8, "avg_cost": None, "concentration": None})
        )
        self.assertTrue(
            NotificationService._has_meaningful_chip({"profit_ratio": None, "avg_cost": "10.5", "concentration": None})
        )
        self.assertTrue(
            NotificationService._has_meaningful_chip({"profit_ratio": "N/A", "avg_cost": "N/A", "concentration": 0.12})
        )


class TestGenerateDashboardReportContent(unittest.TestCase):
    """Test that generate_dashboard_report omits 量能/筹码 when N/A and includes MACD/RSI + 解读 when present."""

    def setUp(self):
        self.notifier = NotificationService()

    def _result_with_dashboard(self, data_perspective):
        return AnalysisResult(
            code="600519",
            name="贵州茅台",
            sentiment_score=60,
            trend_prediction="看多",
            operation_advice="持有",
            dashboard={"data_perspective": data_perspective, "battle_plan": {}, "core_conclusion": {}},
        )

    def test_report_omits_vol_when_all_none(self):
        data_persp = {
            "trend_status": {"ma_alignment": "多头", "is_bullish": True},
            "price_position": {"current_price": 1800, "ma5": 1790},
            "volume_analysis": {"volume_ratio": None, "volume_status": "", "turnover_rate": None, "volume_meaning": ""},
            "chip_structure": {"profit_ratio": None, "avg_cost": None, "concentration": None, "chip_health": "健康"},
        }
        report = self.notifier.generate_dashboard_report([self._result_with_dashboard(data_persp)])
        self.assertIn("数据透视", report)
        # When vol_data has no meaningful values, the 量能 block is not emitted at all.
        self.assertNotIn("**量能**:", report)

    def test_report_omits_chip_when_all_none(self):
        data_persp = {
            "trend_status": {"ma_alignment": "多头", "is_bullish": True},
            "price_position": {"current_price": 1800},
            "volume_analysis": {"volume_ratio": 1.2, "turnover_rate": 5},
            "chip_structure": {"profit_ratio": None, "avg_cost": None, "concentration": None, "chip_health": "健康"},
        }
        report = self.notifier.generate_dashboard_report([self._result_with_dashboard(data_persp)])
        self.assertIn("**量能**:", report)
        # When chip_data has no meaningful values, the 筹码 block is not emitted.
        self.assertNotIn("**筹码**:", report)

    def test_report_includes_macd_rsi_and_interpretation_when_present(self):
        data_persp = {
            "trend_status": {"ma_alignment": "多头", "is_bullish": True},
            "price_position": {"current_price": 1800},
            "macd": {"dif": 0.1, "dea": 0.05, "bar": 0.1, "signal": "金叉，趋势向上"},
            "rsi": {"rsi_6": 55, "rsi_12": 52, "rsi_24": 50, "signal": "RSI中性"},
            "tech_interpretation": "MACD 金叉支撑做多，RSI 中性无超买超卖，可结合均线持有。",
        }
        report = self.notifier.generate_dashboard_report([self._result_with_dashboard(data_persp)])
        self.assertIn("**MACD**:", report)
        self.assertIn("**RSI**:", report)
        self.assertIn("💡 **解读**:", report)
        self.assertIn("MACD 金叉支撑做多", report)


if __name__ == "__main__":
    unittest.main()
