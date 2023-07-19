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

    def test_e2e_rapidcapr_improvement_over_capr_with_gpt35_on_d4j_Time_4(self):
        project = "Time"
        bug_id = 4

        test_validate_patch_cache = Path(__file__).parent.parent / 'cache' / 'validate_patch_cache' # Uses prod cache (insead of test cache)
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
        
        capr_token_usage_on_Time_4 = 210000 # Authors average
        capr_Time_4_plausible_patch_count = 10 # My reproduced results

        bug = framework.get_bug_details(project, bug_id)

        if bug.bug_type != "OT":
            repair_results = rapidcapr.repair(bug=bug, max_fpps_try_per_mode=5, max_mpps_try_per_mode=5,
                                                prompt_token_limit=2048, total_token_limit_target=4096,
                                                similarity_threshold=0.5)
            plausible_patches, _, repair_cost, _, _, _, _, _ = repair_results

            rapidcapr_token_usage_on_Time_4 = repair_cost
            rapidcapr_Time_4_plausible_patch_count = len(plausible_patches)

        self.assertLessEqual(rapidcapr_token_usage_on_Time_4, capr_token_usage_on_Time_4) # 16848 < 42000
        self.assertGreaterEqual(rapidcapr_Time_4_plausible_patch_count, capr_Time_4_plausible_patch_count) # 8 not > 10
