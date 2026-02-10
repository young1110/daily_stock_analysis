# -*- coding: utf-8 -*-
"""
Tests for pipeline _enhance_context: trend_analysis includes macd_*, rsi_* when trend_result has them.
"""

import os
import tempfile
import unittest

from src.config import Config
from src.storage import DatabaseManager
from src.core.pipeline import StockAnalysisPipeline
from src.stock_analyzer import TrendAnalysisResult, TrendStatus, VolumeStatus, BuySignal


class PipelineEnhanceContextTestCase(unittest.TestCase):
    """Test _enhance_context adds MACD/RSI to trend_analysis when trend_result has them."""

    def setUp(self):
        self._temp_dir = tempfile.TemporaryDirectory()
        self._db_path = os.path.join(self._temp_dir.name, "test_pipeline.db")
        os.environ["DATABASE_PATH"] = self._db_path
        Config._instance = None
        DatabaseManager.reset_instance()
        self.pipeline = StockAnalysisPipeline()

    def tearDown(self):
        DatabaseManager.reset_instance()
        self._temp_dir.cleanup()

    def test_enhance_context_includes_macd_rsi_from_trend_result(self):
        trend_result = TrendAnalysisResult(
            code="600519",
            trend_status=TrendStatus.BULL,
            ma_alignment="MA5>MA10>MA20",
            trend_strength=75.0,
            volume_status=VolumeStatus.NORMAL,
            buy_signal=BuySignal.HOLD,
            macd_dif=0.12,
            macd_dea=0.06,
            macd_bar=0.06,
            macd_signal="金叉，多头",
            rsi_6=55.0,
            rsi_12=52.0,
            rsi_24=50.0,
            rsi_signal="RSI中性",
        )
        enhanced = self.pipeline._enhance_context(
            context={},
            realtime_quote=None,
            chip_data=None,
            trend_result=trend_result,
            stock_name="贵州茅台",
        )
        self.assertIn("trend_analysis", enhanced)
        ta = enhanced["trend_analysis"]
        self.assertEqual(ta["macd_dif"], 0.12)
        self.assertEqual(ta["macd_dea"], 0.06)
        self.assertEqual(ta["macd_bar"], 0.06)
        self.assertEqual(ta["macd_signal"], "金叉，多头")
        self.assertEqual(ta["rsi_6"], 55.0)
        self.assertEqual(ta["rsi_12"], 52.0)
        self.assertEqual(ta["rsi_24"], 50.0)
        self.assertEqual(ta["rsi_signal"], "RSI中性")
        self.assertEqual(ta["trend_status"], TrendStatus.BULL.value)

    def test_enhance_context_trend_analysis_absent_when_no_trend_result(self):
        enhanced = self.pipeline._enhance_context(
            context={},
            realtime_quote=None,
            chip_data=None,
            trend_result=None,
            stock_name="贵州茅台",
        )
        self.assertNotIn("trend_analysis", enhanced)


if __name__ == "__main__":
    unittest.main()
