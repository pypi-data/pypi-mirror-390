import os
import unittest

from ketacli.sdk.convert_ir.spl_parser import parse_spl
from ketacli.sdk.convert_ir.spl_generator import to_spl

EXAMPLE_PATH = os.path.join(os.path.dirname(__file__), "..", "ai", "prompts", "log_search_example.md")


def load_examples():
    examples = []
    cur = None
    if not os.path.exists(EXAMPLE_PATH):
        raise FileNotFoundError(f"示例文件不存在: {EXAMPLE_PATH}")
    with open(EXAMPLE_PATH, 'r', encoding='utf-8') as f:
        for line in f:
            s = line.strip()
            if not s:
                if cur:
                    examples.append(cur)
                    cur = None
                continue
            if s.startswith('search2'):
                if cur:
                    examples.append(cur)
                cur = s
            elif s.startswith('|') and cur:
                cur += ' ' + s
            else:
                # 其他情况（不以 search2 或管道开头），可能是断行错误或说明，直接拼接
                if cur:
                    cur += ' ' + s
        if cur:
            examples.append(cur)
    return examples


class TestSPLExamples(unittest.TestCase):
    def setUp(self):
        self.examples = load_examples()
        self.assertGreater(len(self.examples), 0)

    def test_parse_and_normalize_examples(self):
        for i, spl in enumerate(self.examples):
            with self.subTest(case=i):
                pipe = parse_spl(spl)
                normalized = to_spl(pipe)
                # 规范化幂等：再次解析再渲染应不变
                normalized2 = to_spl(parse_spl(normalized))
                self.assertEqual(normalized, normalized2)
                # 不应包含 filter，统一使用 where
                self.assertNotIn(' filter ', ' ' + normalized + ' ')
                # 括号匹配
                self.assertEqual(normalized.count('('), normalized.count(')'))
                # 如果包含 start 与 repo，确保顺序正确（start 在 repo 前）
                if 'start="' in normalized and 'repo="' in normalized:
                    self.assertLess(normalized.index('start="'), normalized.index('repo="'))
                # 如果包含 sort N by，保持不丢失数量
                if ' sort ' in normalized and ' by ' in normalized:
                    # 只检查存在示例中的 "sort 10 by" 不被移除
                    if 'sort 10 by' in spl:
                        self.assertIn('sort 10 by', normalized)


if __name__ == '__main__':
    unittest.main()