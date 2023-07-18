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

    def test_e2e_rapidcapr_improvement_over_capr_with_gpt35_on_d4j_Time(self):
        project = "Time"
        # ids = [i for i in range(1, 28) if i != 21]
        ids = [4]

        test_validate_patch_cache = Path(__file__).parent / 'cache' / 'validate_patch'
        test_n_shot_cache = Path(__file__).parent / 'cache' / 'n_shot'
        test_bug_details_cache = Path(__file__).parent / 'cache' / 'bug_details'
        test_gpt35_cache_folder = Path(__file__).parent / 'cache' / 'gpt35'

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
                repair_results = rapidcapr.repair(bug=bug, max_fpps_try_per_mode=1, max_mpps_try_per_mode=1, 
                                                  prompt_tokens_limit=1500, completion_tokens_limit=1500, 
                                                  similarity_threshold=0.5)
                plausible_patches, _, repair_cost, _, _, _, _, _ = repair_results

                rapidcapr_token_usage_on_Time += repair_cost
                if len(plausible_patches) > 0:
                    rapidcapr_Time_bugs_with_plausible_patches += 1

        self.assertLessEqual(rapidcapr_token_usage_on_Time, capr_token_usage_on_Time / 2)
        self.assertGreaterEqual(rapidcapr_Time_bugs_with_plausible_patches, capr_Time_bugs_with_plausible_patches)
