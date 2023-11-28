import argparse
from src.capr import Capr
from src.rapidcapr import RapidCapr
from src.chatgpt import ChatGPT
from src.framework import Framework
from src.analysis import Analysis
from prog_params import ProgParams as prog_params
from user_params import UserParams as user_params

def main(framework=None, project=None, bug_ids=None, repair_tool=None):

    defects4j = Framework(name="defects4j", list_of_bugs = prog_params.d4j_list_of_bugs, 
                            d4j_path=user_params.D4J_PATH, java_home=user_params.JAVA_HOME, tmp_dir=user_params.TMP_DIR,
                            validate_patch_cache_folder=prog_params.validate_patch_cache_folder,
                            n_shot_cache_folder=prog_params.n_shot_cache_folder,
                            bug_details_cache_folder=prog_params.bug_details_cache_folder)
    human_eval_java = Framework(name="humanevaljava", # TODO add human eval java framework
                                list_of_bugs=user_params.humaneval_list_of_bugs,
                                d4j_path=user_params.HUMANEVAL_PATH,
                                java_home=user_params.JAVA_HOME,
                                tmp_dir=user_params.TMP_DIR,
                                validate_patch_cache_folder=prog_params.validate_patch_cache_folder,
                                n_shot_cache_folder=prog_params.n_shot_cache_folder,
                                bug_details_cache_folder=prog_params.bug_details_cache_folder) 
    chatgpt = ChatGPT(model=prog_params.gpt35_model, api_key=user_params.API_KEY,
                    cache_folder=prog_params.gpt35_cache_folder,
                    load_from_cache=True, save_to_cache=True)
    
    frameworks = [defects4j, human_eval_java]
    if framework is not None:
        frameworks = [f for f in frameworks if f.name == framework]
    
    for test_framework in frameworks:

        capr = Capr(chatgpt=chatgpt, framework=test_framework)
        rapidcapr = RapidCapr(chatgpt=chatgpt, framework=test_framework)
        
        aprs = [capr, rapidcapr]
        if repair_tool is not None:
            aprs = [apr for apr in aprs if apr.name.lower() == repair_tool]

        for apr in aprs:
        
            if project is not None and bug_ids is not None:
                list_of_bugs_to_fix = [(project, bug_ids)]
            elif project is not None:
                if test_framework.name == "defects4j":
                    list_of_bugs_to_fix = [(project, [ids for proj, ids in prog_params.d4j_list_of_bugs if proj == project][0])]
                elif test_framework.name == "human_eval_java":
                    pass # TODO add human eval java framework
            else:
                if test_framework.name == "defects4j":
                    list_of_bugs_to_fix = prog_params.d4j_list_of_bugs
                elif test_framework.name == "human_eval_java":
                    pass # TODO add human eval java framework
            
            analysis = Analysis(apr=apr, framework=test_framework)
            analysis.run(list_of_bugs_to_fix)


if __name__ == '__main__':

    project_choices = [p for p, _ in prog_params.d4j_list_of_bugs]

    parser = argparse.ArgumentParser(description='Run CAPR on D4J Bugs')

    parser.add_argument('-fr', '--framework', metavar='path', required=False, help='Framework to use', choices=['defects4j', 'human_eval_java'])
    parser.add_argument('-p', '--proj', metavar='path', required=False, help='Project name', choices=project_choices)
    parser.add_argument('-bs', '--bug_ids', metavar='path', required=False, help='List of bug_ids to repair', type=int, nargs='+')
    parser.add_argument('-apr', '--repair_tool', metavar='path', required=False, help='APR algorithms to use', choices=['capr', 'rapidcapr'])
    
    args = parser.parse_args()

    main(framework=args.framework, project=args.proj, bug_ids=args.bug_ids, repair_tool=args.repair_tool)
