import unittest

from ketacli.sdk.convert_ir.spl_parser import parse_spl
from ketacli.sdk.convert_ir.spl_generator import to_spl, render_filter_expr
from ketacli.sdk.convert_ir.ir import BoolExpr, Filter


class TestSPLBooleanParsing(unittest.TestCase):
    def test_search2_or_parentheses_preserved(self):
        spl = 'search2 start="2025-10-15" repo="log-repo" origin="_collector" (infra_type = "vm" OR service = "core")'
        pipe = parse_spl(spl)
        # 断言有一个 search2 阶段
        self.assertGreaterEqual(len(pipe.stages), 1)
        search = pipe.stages[0]
        self.assertEqual(getattr(search, 'start', None), '2025-10-15')
        self.assertEqual(getattr(search, 'repo', None), 'log-repo')
        # 查询表达式应该是 and，包含 eq(origin) 与 or(infra_type, service)
        expr = search.query
        self.assertIsInstance(expr, BoolExpr)
        self.assertEqual(expr.op, 'and')
        self.assertEqual(len(expr.children), 2)
        self.assertIsInstance(expr.children[0], Filter)
        self.assertEqual(expr.children[0].op, 'eq')
        self.assertEqual(expr.children[0].field, 'origin')
        self.assertEqual(expr.children[0].value, '_collector')
        # 第二个子节点是 OR 表达式，校验两个操作数
        or_node = expr.children[1]
        self.assertIsInstance(or_node, BoolExpr)
        self.assertEqual(or_node.op, 'or')
        self.assertEqual(len(or_node.children), 2)
        self.assertEqual(or_node.children[0].field, 'infra_type')
        self.assertEqual(or_node.children[0].op, 'eq')
        self.assertEqual(or_node.children[0].value, 'vm')
        self.assertEqual(or_node.children[1].field, 'service')
        self.assertEqual(or_node.children[1].op, 'eq')
        # 注意：service 的值会是 core（无多余右括号）
        self.assertEqual(or_node.children[1].value, 'core')
        # 标准化输出应保留 OR 与括号
        normalized = to_spl(pipe)
        self.assertIn("('infra_type' = \"vm\" OR 'service' = \"core\")", normalized)
        self.assertIn("'origin' = \"_collector\" AND", normalized)
        self.assertTrue(normalized.startswith('search2 start="2025-10-15" repo="log-repo"'))
        # 渲染查询子串不应包含多余的右括号
        rendered_query = render_filter_expr(expr)
        self.assertEqual(rendered_query.count('('), rendered_query.count(')'))

    def test_where_and_or_parentheses_injection(self):
        # 测试 where 阶段括号保留与优先级： (A OR B) AND C
        spl = 'search2 origin="_collector" | where (infra_type = "vm" OR service = "core") AND repoName = "prod"'
        pipe = parse_spl(spl)
        self.assertEqual(len(pipe.stages), 2)
        where = pipe.stages[1]
        expr = where.expr
        self.assertIsInstance(expr, BoolExpr)
        self.assertEqual(expr.op, 'and')
        # 左侧 OR 子表达式
        left = expr.children[0]
        right = expr.children[1]
        self.assertIsInstance(left, BoolExpr)
        self.assertEqual(left.op, 'or')
        self.assertIsInstance(right, Filter)
        self.assertEqual(right.field, 'repoName')
        normalized = to_spl(pipe)
        # 应包含括号分组的 OR 子表达式
        self.assertIn("where ('infra_type' = \"vm\" OR 'service' = \"core\") AND 'repoName' = \"prod\"", normalized)


if __name__ == '__main__':
    unittest.main()