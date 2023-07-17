import unittest
from src.utils import synthetize_and_extract_patch

class TestRapidCapr(unittest.TestCase):

    def test_synthetize_and_extract_patch(self):
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