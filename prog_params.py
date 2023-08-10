import logging
from pathlib import Path

class ProgParams:

    ### Framework related
    shell_script_folder = Path(__file__).parent / "frameworks"
    validate_patch_cache_folder=Path(__file__).parent / 'cache' / 'validate_patch_cache'
    bug_details_cache_folder=Path(__file__).parent / 'cache' / 'bug_details_cache'
    n_shot_cache_folder=Path(__file__).parent / 'cache' / 'n_shot_cache'
    # Defects4J related
    d4j_list_of_bugs = [("Chart", [i for i in range(1, 27)]),
                        ("Closure", [i for i in range(1, 177) if i != 63 and i != 93]),
                        ("Lang", [i for i in range(1, 66) if i != 2]),
                        ("Math", [i for i in range(1, 107)]),
                        ("Mockito", [i for i in range(1, 39)]),
                        ("Time", [i for i in range(1, 28) if i != 21])]
    
    ### LLM Related
    # ChatGPT related
    gpt35_model = "gpt-3.5-turbo-0301"
    gpt35_model_token_limit = 4097
    gpt35_cache_folder=Path(__file__).parent / 'cache' / 'chatgpt_cache'

    ### Algorithm Related
    # CAPR related
    capr_SL_SH_max_tries = 200
    capr_SF_max_tries = 100
    capr_n_shot_count = 1
    capr_max_conv_length = 3
    # RapidCapr related
    rapidcapr_max_fpps_try_per_mode = 5
    rapidcapr_max_mpps_try_per_mode = 5
    rapidcapr_prompt_token_limit = 1500
    rapidcapr_total_token_limit_target = 3000
    rapidcapr_max_sample_count = 100
    rapidcapr_similarity_threshold = 0.5
    rapidcapr_max_rounds = 9

    ### Logging Parameters ###
    logging_level=logging.INFO