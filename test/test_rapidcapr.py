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
        
        self.max_fpps_try_per_mode = prog_params.rapidcapr_max_fpps_try_per_mode
        self.max_mpps_try_per_mode = prog_params.rapidcapr_max_mpps_try_per_mode
        self.prompt_token_limit = prog_params.rapidcapr_prompt_token_limit
        self.total_token_limit_target = prog_params.rapidcapr_total_token_limit_target
        self.max_sample_count = prog_params.rapidcapr_max_sample_count
        self.similarity_threshold = prog_params.rapidcapr_similarity_threshold

    def test_e2e_rapidcapr_improvement_over_capr_with_gpt35_on_d4j_Time_4(self):
        project = "Time"
        bug_id = 4

        test_validate_patch_cache = Path(__file__).parent.parent / 'cache' / 'validate_patch_cache' # Uses prod cache (instead of test cache)
        test_n_shot_cache = Path(__file__).parent.parent / 'cache' / 'n_shot_cache' # Uses prod cache (instead of test cache)
        test_bug_details_cache = Path(__file__).parent.parent / 'cache' / 'bug_details_cache' # Uses prod cache (instead of test cache)
        test_gpt35_cache_folder = Path(__file__).parent / 'cache' / 'gpt35'

        framework = Framework(name="defects4j", list_of_bugs = prog_params.d4j_list_of_bugs, 
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
            repair_results = rapidcapr.repair(bug=bug, max_fpps_try_per_mode=self.max_fpps_try_per_mode, max_mpps_try_per_mode=self.max_mpps_try_per_mode,
                                                prompt_token_limit=self.prompt_token_limit, total_token_limit_target=self.total_token_limit_target,
                                                max_sample_count=self.max_sample_count, similarity_threshold=self.similarity_threshold, max_rounds=1)
            plausible_patches, _, repair_cost, _, _, _, _, _ = repair_results

            rapidcapr_token_usage_on_Time_4 = repair_cost
            rapidcapr_Time_4_plausible_patch_count = len(plausible_patches)

        self.assertLessEqual(rapidcapr_token_usage_on_Time_4, capr_token_usage_on_Time_4 / 5)
        self.assertGreaterEqual(rapidcapr_Time_4_plausible_patch_count, capr_Time_4_plausible_patch_count)

    def test_e2e_rapidcapr_improvement_over_capr_with_gpt35_on_d4j_Closure_86(self):
        project = "Closure"
        bug_id = 86

        test_validate_patch_cache = Path(__file__).parent.parent / 'cache' / 'validate_patch_cache' # Uses prod cache (instead of test cache)
        test_n_shot_cache = Path(__file__).parent.parent / 'cache' / 'n_shot_cache' # Uses prod cache (instead of test cache)
        test_bug_details_cache = Path(__file__).parent.parent / 'cache' / 'bug_details_cache' # Uses prod cache (instead of test cache)
        test_gpt35_cache_folder = Path(__file__).parent / 'cache' / 'gpt35'

        framework = Framework(name="defects4j", list_of_bugs = prog_params.d4j_list_of_bugs, 
                          d4j_path=user_params.D4J_PATH, java_home=user_params.JAVA_HOME, tmp_dir=user_params.TMP_DIR,
                          validate_patch_cache_folder=test_validate_patch_cache,
                          n_shot_cache_folder=test_n_shot_cache,
                          bug_details_cache_folder=test_bug_details_cache)
        chatgpt = ChatGPT(model=prog_params.gpt35_model, api_key=user_params.API_KEY,
                        cache_folder=test_gpt35_cache_folder,
                        load_from_cache=True, save_to_cache=True)
        rapidcapr = RapidCapr(chatgpt=chatgpt,
                              framework=framework)
        
        capr_token_usage_on_Closure_86 = 210000 # Authors average
        capr_Closure_86_plausible_patch_count = 29 # My reproduced results

        bug = framework.get_bug_details(project, bug_id)

        if bug.bug_type != "OT":
            repair_results = rapidcapr.repair(bug=bug, max_fpps_try_per_mode=self.max_fpps_try_per_mode, max_mpps_try_per_mode=self.max_mpps_try_per_mode,
                                                prompt_token_limit=self.prompt_token_limit, total_token_limit_target=self.total_token_limit_target,
                                                max_sample_count=self.max_sample_count, similarity_threshold=self.similarity_threshold)
            plausible_patches, _, repair_cost, _, _, _, _, _ = repair_results

            rapidcapr_token_usage_on_Closure_86 = repair_cost
            rapidcapr_Closure_86_plausible_patch_count = len(plausible_patches)

        self.assertLessEqual(rapidcapr_token_usage_on_Closure_86, capr_token_usage_on_Closure_86 / 5)
        self.assertGreaterEqual(rapidcapr_Closure_86_plausible_patch_count, capr_Closure_86_plausible_patch_count)

    def test_e2e_rapidcapr_improvement_over_capr_with_gpt35_on_d4j_Chart_6(self):
        project = "Chart"
        bug_id = 6 # SH

        test_validate_patch_cache = Path(__file__).parent.parent / 'cache' / 'validate_patch_cache' # Uses prod cache (instead of test cache)
        test_n_shot_cache = Path(__file__).parent.parent / 'cache' / 'n_shot_cache' # Uses prod cache (instead of test cache)
        test_bug_details_cache = Path(__file__).parent.parent / 'cache' / 'bug_details_cache' # Uses prod cache (instead of test cache)
        test_gpt35_cache_folder = Path(__file__).parent / 'cache' / 'gpt35'

        framework = Framework(name="defects4j", list_of_bugs = prog_params.d4j_list_of_bugs, 
                          d4j_path=user_params.D4J_PATH, java_home=user_params.JAVA_HOME, tmp_dir=user_params.TMP_DIR,
                          validate_patch_cache_folder=test_validate_patch_cache,
                          n_shot_cache_folder=test_n_shot_cache,
                          bug_details_cache_folder=test_bug_details_cache)
        chatgpt = ChatGPT(model=prog_params.gpt35_model, api_key=user_params.API_KEY,
                        cache_folder=test_gpt35_cache_folder,
                        load_from_cache=True, save_to_cache=True)
        rapidcapr = RapidCapr(chatgpt=chatgpt,
                              framework=framework)
        
        capr_token_usage_on_Chart_6 = 210000 # Authors average
        capr_Chart_6_plausible_patch_count = 30 # My reproduced results

        bug = framework.get_bug_details(project, bug_id)

        if bug.bug_type != "OT":
            repair_results = rapidcapr.repair(bug=bug, max_fpps_try_per_mode=self.max_fpps_try_per_mode, max_mpps_try_per_mode=self.max_mpps_try_per_mode,
                                                prompt_token_limit=self.prompt_token_limit, total_token_limit_target=self.total_token_limit_target,
                                                max_sample_count=self.max_sample_count, similarity_threshold=self.similarity_threshold)
            plausible_patches, _, repair_cost, _, _, _, _, _ = repair_results

            rapidcapr_token_usage_on_Chart_6 = repair_cost
            rapidcapr_Chart_6_plausible_patch_count = len(plausible_patches)

        self.assertLessEqual(rapidcapr_token_usage_on_Chart_6, capr_token_usage_on_Chart_6 / 5)
        self.assertGreaterEqual(rapidcapr_Chart_6_plausible_patch_count, capr_Chart_6_plausible_patch_count)

    def test_e2e_rapidcapr_improvement_over_capr_with_gpt35_on_d4j_Chart_7(self):
        project = "Chart"
        bug_id = 7 # SF

        test_validate_patch_cache = Path(__file__).parent.parent / 'cache' / 'validate_patch_cache' # Uses prod cache (instead of test cache)
        test_n_shot_cache = Path(__file__).parent.parent / 'cache' / 'n_shot_cache' # Uses prod cache (instead of test cache)
        test_bug_details_cache = Path(__file__).parent.parent / 'cache' / 'bug_details_cache' # Uses prod cache (instead of test cache)
        test_gpt35_cache_folder = Path(__file__).parent / 'cache' / 'gpt35'

        framework = Framework(name="defects4j", list_of_bugs = prog_params.d4j_list_of_bugs, 
                          d4j_path=user_params.D4J_PATH, java_home=user_params.JAVA_HOME, tmp_dir=user_params.TMP_DIR,
                          validate_patch_cache_folder=test_validate_patch_cache,
                          n_shot_cache_folder=test_n_shot_cache,
                          bug_details_cache_folder=test_bug_details_cache)
        chatgpt = ChatGPT(model=prog_params.gpt35_model, api_key=user_params.API_KEY,
                        cache_folder=test_gpt35_cache_folder,
                        load_from_cache=True, save_to_cache=True)
        rapidcapr = RapidCapr(chatgpt=chatgpt,
                              framework=framework)
        
        capr_token_usage_on_Chart_7 = 210000 # Authors average
        capr_Chart_7_plausible_patch_count = 8 # My reproduced results

        bug = framework.get_bug_details(project, bug_id)

        if bug.bug_type != "OT":
            repair_results = rapidcapr.repair(bug=bug, max_fpps_try_per_mode=self.max_fpps_try_per_mode, max_mpps_try_per_mode=self.max_mpps_try_per_mode,
                                                prompt_token_limit=self.prompt_token_limit, total_token_limit_target=self.total_token_limit_target,
                                                max_sample_count=self.max_sample_count, similarity_threshold=self.similarity_threshold)
            plausible_patches, _, repair_cost, _, _, _, _, _ = repair_results

            rapidcapr_token_usage_on_Chart_6 = repair_cost
            rapidcapr_Chart_6_plausible_patch_count = len(plausible_patches)

        self.assertLessEqual(rapidcapr_token_usage_on_Chart_6, capr_token_usage_on_Chart_7 / 5)
        self.assertGreaterEqual(rapidcapr_Chart_6_plausible_patch_count, capr_Chart_7_plausible_patch_count)

    @unittest.skip("The GetBugExplanation feature did not increase the results")
    def test_e2e_rapidcapr_ask_for_bug_description_improvement(self):

        capr_bugs_with_plausible_patch = 0
        rapidcapr_bugs_with_plausible_patch = 0

        for project, bug_id in [("Lang", 6)]:

            test_validate_patch_cache = Path(__file__).parent.parent / 'cache' / 'validate_patch_cache' # Uses prod cache (instead of test cache)
            test_n_shot_cache = Path(__file__).parent.parent / 'cache' / 'n_shot_cache' # Uses prod cache (instead of test cache)
            test_bug_details_cache = Path(__file__).parent.parent / 'cache' / 'bug_details_cache' # Uses prod cache (instead of test cache)
            test_gpt35_cache_folder = Path(__file__).parent / 'cache' / 'gpt35'

            framework = Framework(name="defects4j", list_of_bugs = prog_params.d4j_list_of_bugs, 
                            d4j_path=user_params.D4J_PATH, java_home=user_params.JAVA_HOME, tmp_dir=user_params.TMP_DIR,
                            validate_patch_cache_folder=test_validate_patch_cache,
                            n_shot_cache_folder=test_n_shot_cache,
                            bug_details_cache_folder=test_bug_details_cache)
            chatgpt = ChatGPT(model=prog_params.gpt35_model, api_key=user_params.API_KEY,
                            cache_folder=test_gpt35_cache_folder,
                            load_from_cache=True, save_to_cache=True)
            rapidcapr = RapidCapr(chatgpt=chatgpt,
                                framework=framework)

            bug = framework.get_bug_details(project, bug_id)

            if bug.bug_type != "OT":
                repair_results = rapidcapr.repair(bug=bug, max_fpps_try_per_mode=self.max_fpps_try_per_mode, max_mpps_try_per_mode=0,
                                                    prompt_token_limit=self.prompt_token_limit, total_token_limit_target=self.total_token_limit_target,
                                                    max_sample_count=self.max_sample_count, similarity_threshold=self.similarity_threshold,
                                                    ask_for_bug_description=True)
                plausible_patches, _, _, _, _, _, _, _ = repair_results

                if len(plausible_patches) > 0 :
                    rapidcapr_bugs_with_plausible_patch += 1
                    break

        self.assertGreater(rapidcapr_bugs_with_plausible_patch, capr_bugs_with_plausible_patch)
