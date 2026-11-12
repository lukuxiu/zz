import os
import sys
import json
import unittest

class TestMilestone1(unittest.TestCase):
    def setUp(self):
        self.json_path = "data/knowledge.json"
        with open(self.json_path, "r", encoding="utf-8") as f:
            self.kb = json.load(f)
        self.records = self.kb.get("records", [])

    def test_json_validity_and_completeness(self):
        """测试 JSON 结构与字段完整性"""
        self.assertTrue(os.path.exists(self.json_path))
        self.assertEqual(len(self.records), 122, f"卡片数量应为 122，实际为 {len(self.records)}")
        for r in self.records:
            self.assertIn("id", r)
            self.assertIn("sourceId", r)
            self.assertIn("title", r)
            self.assertIn("content", r)
            self.assertIn("keywords", r)
            self.assertIn("sourcePage", r)
            self.assertIn("sourceImages", r)

    def test_source_id_continuity(self):
        """测试 001-100 连续无缺失"""
        sids = set(r["sourceId"] for r in self.records if r["sourceId"] != "unknown")
        self.assertEqual(len(sids), 100, f"原书编号唯一数应为 100，实际为 {len(sids)}")
        for i in range(1, 101):
            expected_id = f"{i:03d}"
            self.assertIn(expected_id, sids, f"缺少编号 {expected_id}")

    def test_duplicate_source_ids(self):
        """测试 21 个重复编号及出现次数"""
        from collections import Counter
        counts = Counter(r["sourceId"] for r in self.records)
        dups = {k: v for k, v in counts.items() if v > 1}
        self.assertEqual(len(dups), 21, f"重复编号数量应为 21 个，实际为 {len(dups)}")
        self.assertEqual(counts["080"], 3, "知识点 080 应出现 3 次")
        self.assertEqual(counts["005"], 2, "知识点 005 应出现 2 次")

    def test_cropped_images_existence_and_integrity(self):
        """测试 122 张卡片裁切图片存在性及有效性"""
        for r in self.records:
            self.assertTrue(len(r["sourceImages"]) > 0, f"记录 {r['id']} 缺少图片路径")
            for img_rel in r["sourceImages"]:
                full_path = os.path.join("public", img_rel)
                self.assertTrue(os.path.exists(full_path), f"裁切图片未找到: {full_path}")
                self.assertGreater(os.path.getsize(full_path), 1024, f"裁切图片过小: {full_path}")

    def test_muted_colors_isolation(self):
        """测试 0xaaaaaa 弱化文字严格隔离"""
        for r in self.records:
            for kw in r["keywords"]:
                self.assertNotEqual(kw.get("colorInt"), 0xaaaaaa, f"记录 {r['id']} 包含弱化文字关键词: {kw['word']}")

    def test_distinctions_verdict_values(self):
        """测试辨析 verdict 仅限 correct/wrong/None"""
        allowed = {"correct", "wrong", None}
        for r in self.records:
            for d in r["distinctions"]:
                self.assertIn(d["verdict"], allowed, f"辨析 verdict 非法: {d['verdict']} 在 {r['id']}")

    def test_required_documents_and_tools(self):
        """测试文档与工具文件存在性"""
        self.assertTrue(os.path.exists("docs/color-semantics.md"))
        self.assertTrue(os.path.exists("docs/symbol-mapping.md"))
        self.assertTrue(os.path.exists("reports/validation.md"))
        self.assertTrue(os.path.exists("tools/review_workbench.html"))

if __name__ == "__main__":
    unittest.main()
