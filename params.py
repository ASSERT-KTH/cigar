from pathlib import Path

class Params:

    ### User Specific
    # Path to the directory where the Defects4J framework is located
    D4J_PATH = "/Users/davidhidvegi/Desktop/defects4j/framework/bin"
    # Path to the directory where the bugs are checked out
    TMP_DIR = "/tmp/defects4j"

    ### Program Specific
    ## Cache related
    validate_patch_cache_folder=Path(__file__).parent / 'data' / 'validate_patch_cache'
    n_shot_cache_folder=Path(__file__).parent / 'data' / 'n_shot_cache'
    bug_details_cache_folder=Path(__file__).parent / 'data' / 'bug_details_cache'

    ## ChatGPT related
    model = "gpt-3.5-turbo-0301"
    api_key_path=Path(__file__).parent / 'openai_api_key.env'
    chatgpt_cache_folder=Path(__file__).parent / 'data' / 'chatgpt_cache'

    ## CAPR related
    list_of_d4j_bugs = [("Chart", [i for i in range(1, 27)]),
                        ("Closure", [i for i in range(1, 177) if i != 63 and i != 93]),
                        ("Lang", [i for i in range(1, 66) if i != 2]),
                        ("Math", [i for i in range(1, 107)]),
                        ("Mockito", [i for i in range(1, 39)]), # Failed to reproduce bugs on macOS and Ubuntu
                        ("Time", [i for i in range(1, 28) if i != 21])]
    
    # Framework related
    shell_script_folder = Path(__file__).parent / "frameworks"