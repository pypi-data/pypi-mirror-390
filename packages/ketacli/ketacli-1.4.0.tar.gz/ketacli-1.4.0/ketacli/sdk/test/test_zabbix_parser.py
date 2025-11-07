import unittest

from ketacli.sdk.convert_ir.zabbix_parser import parse_zabbix
from ketacli.sdk.convert_ir.ir import SearchStage, FieldsStage, StatsStage, FilterStage
from ketacli.sdk.convert_ir.spl_generator import to_spl


class TestZabbixParser(unittest.TestCase):
    def test_trigger_last_equals_zero(self):
        text = "{web01:net.if.in[eth0].last()}=0"
        pipeline = parse_zabbix(text)
        self.assertTrue(pipeline.stages, "Pipeline stages should not be empty")
        # Expect: search2 -> fields -> stats -> where
        self.assertIsInstance(pipeline.stages[0], SearchStage)
        self.assertIsInstance(pipeline.stages[1], FieldsStage)
        self.assertIsInstance(pipeline.stages[2], StatsStage)
        self.assertIsInstance(pipeline.stages[3], FilterStage)
        # Render SPL to ensure generator compatibility
        spl = to_spl(pipeline)
        self.assertIn("search2", spl)
        self.assertIn("stats", spl)
        self.assertIn("where", spl)

    def test_event_filters_line(self):
        text = "group=web severity>=4 ack=0"
        pipeline = parse_zabbix(text)
        self.assertTrue(pipeline.stages, "Pipeline stages should not be empty")
        self.assertIsInstance(pipeline.stages[0], SearchStage)
        self.assertEqual(pipeline.stages[0].repo, "zabbix_events")
        self.assertIsInstance(pipeline.stages[1], FieldsStage)
        # Render SPL
        spl = to_spl(pipeline)
        self.assertIn('repo="zabbix_events"', spl)
        self.assertIn("fields", spl)


if __name__ == "__main__":
    unittest.main()