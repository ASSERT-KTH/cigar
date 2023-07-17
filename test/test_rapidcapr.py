import unittest
from pathlib import Path
from src.framework import Framework
from src.chatgpt import ChatGPT
from src.rapidcapr import RapidCapr
from prog_params import ProgParams as prog_params
from user_params import UserParams as user_params

class TestRapidCapr(unittest.TestCase):

    def __init__(self, methodName: str = "runTest") -> None:
        super().__init__(methodName)
        self.maxDiff = None

    def test_extract_patches_from_response_on_Chart_1_SH(self):
        framework = Framework(test_framework="defects4j", list_of_bugs=None,
                              d4j_path=user_params.D4J_PATH, java_home=user_params.JAVA_HOME, tmp_dir=user_params.TMP_DIR)
        bug = framework.get_bug_details("Chart", 1)
        rapidcapr = RapidCapr(chatgpt=None, framework=None)
        
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

        patches = rapidcapr.extract_patches_from_response(bug=bug, response=response, response_mode="SH")

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
            

    def test_e2e_rapidcapr_improvement_over_capr_with_gpt35_on_d4j_Time(self):
        project = "Time"
        # ids = [i for i in range(1, 28) if i != 21]
        ids = [1]

        test_validate_patch_cache = Path(__file__).parent / 'validate_patch_cache' / 'rapid_capr_e2e'
        test_n_shot_cache = Path(__file__).parent / 'n_shot_cache' / 'rapid_capr_e2e'
        test_bug_details_cache = Path(__file__).parent / 'bug_details_cache' / 'rapid_capr_e2e'
        test_gpt35_cache_folder = Path(__file__).parent / 'gpt35_cache' / 'rapid_capr_e2e'

        framework = Framework(test_framework="defects4j", list_of_bugs = prog_params.d4j_list_of_bugs, 
                          d4j_path=user_params.D4J_PATH, java_home=user_params.JAVA_HOME, tmp_dir=user_params.TMP_DIR,
                          validate_patch_cache_folder=test_validate_patch_cache,
                          n_shot_cache_folder=test_n_shot_cache,
                          bug_details_cache_folder=test_bug_details_cache)
        chatgpt = ChatGPT(model=prog_params.gpt35_model, api_key=user_params.API_KEY,
                        cache_folder=test_gpt35_cache_folder,
                        load_from_cache=True, save_to_cache=True)
        rapidcapr = RapidCapr(chatgpt=chatgpt,
                              framework=framework)
        
        capr_token_usage_on_Time = 4911480
        capr_Time_bugs_with_plausible_patches = 6

        rapidcapr_token_usage_on_Time = 0
        rapidcapr_Time_bugs_with_plausible_patches = 0

        for bug_id in ids:
            bug = framework.get_bug_details(project, bug_id)

            if bug.bug_type != "OT":
                repair_results = rapidcapr.repair(bug=bug)
                plausible_patches, _, repair_cost, _, _, _, _, _ = repair_results

                rapidcapr_token_usage_on_Time += repair_cost
                if len(plausible_patches) > 0:
                    rapidcapr_Time_bugs_with_plausible_patches += 1

        self.assertLessEqual(rapidcapr_token_usage_on_Time, capr_token_usage_on_Time / 2)
        self.assertGreaterEqual(rapidcapr_Time_bugs_with_plausible_patches, capr_Time_bugs_with_plausible_patches)
