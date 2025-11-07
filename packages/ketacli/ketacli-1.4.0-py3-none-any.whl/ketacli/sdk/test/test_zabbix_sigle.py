import unittest
import os

from ketacli.sdk.convert_ir.zabbix_lexparser import parse_zabbix_lex
from ketacli.sdk.convert_ir.spl_generator import to_spl

CSV_PATH = os.path.join(os.path.dirname(__file__), 'zabbix_sigle.csv')

class TestZabbixSigleRules(unittest.TestCase):
    def _load_lines(self):
        with open(CSV_PATH, 'r', encoding='utf-8') as f:
            return [ln.strip() for ln in f.readlines() if ln.strip()]

    def _convert(self, text: str) -> str:
        pipeline = parse_zabbix_lex(text, default_repo='zabbix')
        return to_spl(pipeline)

    def test_time_function_mapping(self):
        lines = [ln for ln in self._load_lines() if '.time()' in ln]
        self.assertGreater(len(lines), 0)
        for ln in lines:
            spl = self._convert(ln)
            self.assertIn('eval hhmm=hour(_time)*10000 + minute(_time)*100 + second(_time)', spl, msg=f"Missing hhmm extraction via hour/minute/second for: {ln}\n{spl}")

    def test_dayofweek_function_mapping(self):
        lines = [ln for ln in self._load_lines() if '.dayofweek()' in ln]
        self.assertGreater(len(lines), 0)
        for ln in lines:
            spl = self._convert(ln)
            # 期望使用SPL文档支持的布尔函数进行星期判断
            self.assertTrue(('isWeekday(_time)' in spl) or ('isWeekend(_time)' in spl), msg=f"Missing isWeekday/isWeekend for: {ln}\n{spl}")

    def test_str_and_strlen_mappings(self):
        lines = [ln for ln in self._load_lines() if '.str(' in ln or '.strlen()' in ln]
        self.assertGreater(len(lines), 0)
        for ln in lines:
            spl = self._convert(ln)
            if '.strlen()' in ln:
                # strlen() should count occurrences, not inspect string length
                self.assertIn('stats count()', spl, msg=f"Missing count aggregation for strlen() in: {ln}\n{spl}")
                self.assertRegex(spl, r"eval cond_\d=\(cnt [<>=]", msg=f"Missing cond compare on cnt for strlen() in: {ln}\n{spl}")
            if '.str(' in ln:
                # str() should count occurrences (cnt) and compare
                self.assertIn('stats count()', spl, msg=f"Missing count aggregation for str() in: {ln}\n{spl}")
                self.assertRegex(spl, r"eval cond_\d=\(cnt [<>=]", msg=f"Missing cond compare on cnt for str() in: {ln}\n{spl}")

    def test_log_count_aggregate_mapping(self):
        lines = [ln for ln in self._load_lines() if 'log.count' in ln and ('.avg(' in ln or '.sum(' in ln or '.min(' in ln or '.max(' in ln)]
        self.assertGreater(len(lines), 0)
        for ln in lines:
            spl = self._convert(ln)
            # First time-slice count then aggregate over cnt
            self.assertRegex(spl, r"timechart .*count\(\) as cnt", msg=f"Missing base timechart count for log.count source: {ln}\n{spl}")
            self.assertRegex(spl, r"stats (avg|min|max|sum)\(cnt\)", msg=f"Missing aggregate over cnt for: {ln}\n{spl}")

    def test_nodata_mapping(self):
        lines = [ln for ln in self._load_lines() if '.nodata(' in ln]
        self.assertGreater(len(lines), 0)
        for ln in lines:
            spl = self._convert(ln)
            self.assertIn('stats count()', spl, msg=f"Missing count aggregation for nodata in: {ln}\n{spl}")
            # nodata=1 implies cnt==0
            if '}=1' in ln:
                self.assertIn('eval cond_0=(cnt == 0)', spl, msg=f"nodata=1 should compare cnt==0 for: {ln}\n{spl}")

if __name__ == '__main__':
    unittest.main()