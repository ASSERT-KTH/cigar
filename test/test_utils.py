import unittest
from src.framework import Framework
from user_params import UserParams as user_params
from src.utils import synthetize_and_extract_patch, extract_patches_from_response

class TestUtils(unittest.TestCase):

    def test_synthetize_and_extract_patch_on_SH_case(self):
        patch_block = """        if (dataset == null) {
            return result;
        }"""
        masked_code = """    public LegendItemCollection getLegendItems() {
        LegendItemCollection result = new LegendItemCollection();
        if (this.plot == null) {
            return result;
        }
        int index = this.plot.getIndexOf(this);
        CategoryDataset dataset = this.plot.getDataset(index);
>>> [ INFILL ] <<<
            return result;
        }
        int seriesCount = dataset.getRowCount();
        if (plot.getRowRenderingOrder().equals(SortOrder.ASCENDING)) {
            for (int i = 0; i < seriesCount; i++) {
                if (isSeriesVisibleInLegend(i)) {
                    LegendItem item = getLegendItem(index, i);
                    if (item != null) {
                        result.add(item);
                    }
                }
            }
        }
        else {
            for (int i = seriesCount - 1; i >= 0; i--) {
                if (isSeriesVisibleInLegend(i)) {
                    LegendItem item = getLegendItem(index, i);
                    if (item != null) {
                        result.add(item);
                    }
                }
            }
        }
        return result;
    }"""
        buggy_line = """        if (dataset != null) {"""

        expected_patch = "        if (dataset == null) {"

        patch = synthetize_and_extract_patch(patch_block, masked_code, buggy_line)

        self.assertEqual(patch, expected_patch)

    def test_synthetize_and_extract_patch_on_SH_case_on_small_hunk(self):
        patch_block = """        return " title=\"" + ImageMapUtilities.htmlEscape(toolTipText)"""
        masked_code = """    public String generateToolTipFragment(String toolTipText) {
>>> [ INFILL ] <<<
            + "\" alt=\"\"";
    }"""
        buggy_line = """        return " title=\"" + toolTipText"""

        expected_patch = """        return " title=\"" + ImageMapUtilities.htmlEscape(toolTipText)"""

        patch = synthetize_and_extract_patch(patch_block, masked_code, buggy_line)

        self.assertEqual(patch, expected_patch)

    def test_synthetize_and_extract_patch_on_SH_case_on_huge_hunk(self):
        patch_block = """public LegendItemCollection getLegendItems() {
    LegendItemCollection result = new LegendItemCollection();
    if (this.plot == null) {
        return result;
    }
    int index = this.plot.getIndexOf(this);
    CategoryDataset dataset = this.plot.getDataset(index);
    if (dataset == null) {
        return result;
    }
    int seriesCount = dataset.getRowCount();
    if (plot.getRowRenderingOrder().equals(SortOrder.ASCENDING)) {
        for (int i = 0; i < seriesCount; i++) {
            if (isSeriesVisibleInLegend(i)) {
                LegendItem item = getLegendItem(index, i);
                if (item != null) {
                    result.add(item);
                }
            }
        }
    } else {
        for (int i = seriesCount - 1; i >= 0; i--) {
            if (isSeriesVisibleInLegend(i)) {
                LegendItem item = getLegendItem(index, i);
                if (item != null) {
                    result.add(item);
                }
            }
        }
    }
    return result;
}"""
        masked_code = """    public LegendItemCollection getLegendItems() {
        LegendItemCollection result = new LegendItemCollection();
        if (this.plot == null) {
            return result;
        }
        int index = this.plot.getIndexOf(this);
        CategoryDataset dataset = this.plot.getDataset(index);
>>> [ INFILL ] <<<
            return result;
        }
        int seriesCount = dataset.getRowCount();
        if (plot.getRowRenderingOrder().equals(SortOrder.ASCENDING)) {
            for (int i = 0; i < seriesCount; i++) {
                if (isSeriesVisibleInLegend(i)) {
                    LegendItem item = getLegendItem(index, i);
                    if (item != null) {
                        result.add(item);
                    }
                }
            }
        }
        else {
            for (int i = seriesCount - 1; i >= 0; i--) {
                if (isSeriesVisibleInLegend(i)) {
                    LegendItem item = getLegendItem(index, i);
                    if (item != null) {
                        result.add(item);
                    }
                }
            }
        }
        return result;
    }"""
        buggy_line = """        if (dataset != null) {"""

        expected_patch = """public LegendItemCollection getLegendItems() {
    LegendItemCollection result = new LegendItemCollection();
    if (this.plot == null) {
        return result;
    }
    int index = this.plot.getIndexOf(this);
    CategoryDataset dataset = this.plot.getDataset(index);
    if (dataset == null) {
        return result;
    }
    int seriesCount = dataset.getRowCount();
    if (plot.getRowRenderingOrder().equals(SortOrder.ASCENDING)) {
        for (int i = 0; i < seriesCount; i++) {
            if (isSeriesVisibleInLegend(i)) {
                LegendItem item = getLegendItem(index, i);
                if (item != null) {
                    result.add(item);
                }
            }
        }
    } else {
        for (int i = seriesCount - 1; i >= 0; i--) {
            if (isSeriesVisibleInLegend(i)) {
                LegendItem item = getLegendItem(index, i);
                if (item != null) {
                    result.add(item);
                }
            }
        }
    }
    return result;
}"""

        patch = synthetize_and_extract_patch(patch_block, masked_code, buggy_line)

        self.assertEqual(patch, expected_patch)

    def test_synthetize_and_extract_patch_on_SH_case_on_same_code(self):
        patch_block = """    public String generateToolTipFragment(String toolTipText) {
        return " title=\"" + toolTipText
            + "\" alt=\"\"";
    }"""
        masked_code = """    public String generateToolTipFragment(String toolTipText) {
>>> [ INFILL ] <<<
            + "\" alt=\"\"";
    }"""
        buggy_line = """        return " title=\"" + toolTipText"""

        expected_patch = ""

        patch = synthetize_and_extract_patch(patch_block, masked_code, buggy_line)

        self.assertEqual(patch, expected_patch)

    def test_synthetize_and_extract_patch_on_SH_case_on_smaller_same_code(self):
        patch_block = """        return " title=\"" + toolTipText
            + "\" alt=\"\"";"""
        masked_code = """    public String generateToolTipFragment(String toolTipText) {
>>> [ INFILL ] <<<
            + "\" alt=\"\"";
    }"""
        buggy_line = """        return " title=\"" + toolTipText"""

        expected_patch = ""

        patch = synthetize_and_extract_patch(patch_block, masked_code, buggy_line)

        self.assertEqual(patch, expected_patch)

    def test_extract_patches_from_response_on_Chart_1_SH(self):
        framework = Framework(name="defects4j", list_of_bugs=None,
                              d4j_path=user_params.D4J_PATH, java_home=user_params.JAVA_HOME, tmp_dir=user_params.TMP_DIR)
        bug = framework.get_bug_details("Chart", 1)
        
        response = "My apologies for the mistake in my previous infill suggestion. Here's a corrected hunk for the infill location:\n```java\n        if (dataset == null) {\n            return result;\n        }\n``` \nThe full corrected code with the infill at the right position in the `getLegendItems()` method is:\n\n```java\npublic LegendItemCollection getLegendItems() {\n    LegendItemCollection result = new LegendItemCollection();\n    if (this.plot == null) {\n        return result;\n    }\n    int index = this.plot.getIndexOf(this);\n    CategoryDataset dataset = this.plot.getDataset(index);\n    if (dataset == null) {\n        return result;\n    }\n    int seriesCount = dataset.getRowCount();\n    if (plot.getRowRenderingOrder().equals(SortOrder.ASCENDING)) {\n        for (int i = 0; i < seriesCount; i++) {\n            if (isSeriesVisibleInLegend(i)) {\n                LegendItem item = getLegendItem(index, i);\n                if (item != null) {\n                    result.add(item);\n                }\n            }\n        }\n    } else {\n        for (int i = seriesCount - 1; i >= 0; i--) {\n            if (isSeriesVisibleInLegend(i)) {\n                LegendItem item = getLegendItem(index, i);\n                if (item != null) {\n                    result.add(item);\n                }\n            }\n        }\n    }\n    return result;\n}\n``` \n\nI hope this resolves the issue."
        expected_patch_and_mode = [
            ("        if (dataset == null) {\n            return result;\n        }",
             "SH"),
            ("        if (dataset == null) {", 
            "SH"),
            ("public LegendItemCollection getLegendItems() {\n    LegendItemCollection result = new LegendItemCollection();\n    if (this.plot == null) {\n        return result;\n    }\n    int index = this.plot.getIndexOf(this);\n    CategoryDataset dataset = this.plot.getDataset(index);\n    if (dataset == null) {\n        return result;\n    }\n    int seriesCount = dataset.getRowCount();\n    if (plot.getRowRenderingOrder().equals(SortOrder.ASCENDING)) {\n        for (int i = 0; i < seriesCount; i++) {\n            if (isSeriesVisibleInLegend(i)) {\n                LegendItem item = getLegendItem(index, i);\n                if (item != null) {\n                    result.add(item);\n                }\n            }\n        }\n    } else {\n        for (int i = seriesCount - 1; i >= 0; i--) {\n            if (isSeriesVisibleInLegend(i)) {\n                LegendItem item = getLegendItem(index, i);\n                if (item != null) {\n                    result.add(item);\n                }\n            }\n        }\n    }\n    return result;\n}", 
            "SH"),
            ("public LegendItemCollection getLegendItems() {\n    LegendItemCollection result = new LegendItemCollection();\n    if (this.plot == null) {\n        return result;\n    }\n    int index = this.plot.getIndexOf(this);\n    CategoryDataset dataset = this.plot.getDataset(index);\n    if (dataset == null) {\n        return result;\n    }\n    int seriesCount = dataset.getRowCount();\n    if (plot.getRowRenderingOrder().equals(SortOrder.ASCENDING)) {\n        for (int i = 0; i < seriesCount; i++) {\n            if (isSeriesVisibleInLegend(i)) {\n                LegendItem item = getLegendItem(index, i);\n                if (item != null) {\n                    result.add(item);\n                }\n            }\n        }\n    } else {\n        for (int i = seriesCount - 1; i >= 0; i--) {\n            if (isSeriesVisibleInLegend(i)) {\n                LegendItem item = getLegendItem(index, i);\n                if (item != null) {\n                    result.add(item);\n                }\n            }\n        }\n    }\n    return result;\n}", 
            "SF"),
        ]

        patches = extract_patches_from_response(bug=bug, response=response, response_mode="SH", similarity_threshold=0.5)

        self.assertEqual(len(patches), len(expected_patch_and_mode))

        patch_1_code = patches[0][0]
        patch_1_mode = patches[0][1]
        self.assertEqual(patch_1_code, expected_patch_and_mode[0][0])
        self.assertEqual(patch_1_mode, expected_patch_and_mode[0][1])

        patch_2_code = patches[1][0]
        patch_2_mode = patches[1][1]
        self.assertEqual(patch_2_code, expected_patch_and_mode[1][0])
        self.assertEqual(patch_2_mode, expected_patch_and_mode[1][1])

        patch_3_code = patches[2][0]
        patch_3_mode = patches[2][1]
        self.assertEqual(patch_3_code, expected_patch_and_mode[2][0])
        self.assertEqual(patch_3_mode, expected_patch_and_mode[2][1])

        patch_4_code = patches[3][0]
        patch_4_mode = patches[3][1]
        self.assertEqual(patch_4_code, expected_patch_and_mode[3][0])
        self.assertEqual(patch_4_mode, expected_patch_and_mode[3][1])

        self.assertEqual(patches, expected_patch_and_mode)
        