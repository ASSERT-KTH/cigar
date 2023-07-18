class ProposedPatches(object):
    
    def __init__(self):
        self.proposed_patches = []

    def add(self, response, test_result, result_reason, patch_mode, patch, patch_diff):
        for p in self.proposed_patches:
            if p["patch"] == patch and p["patch_mode"] == patch_mode:
                return
        self.proposed_patches.append({"response": response, "test_result": test_result, "result_reason": result_reason, "patch_mode": patch_mode, "patch": patch, "patch_diff": patch_diff})

    def contains_plausible_patch(self, mode):
        for p in self.proposed_patches:
            if p["test_result"] == "PASS" and p["patch_mode"] == mode:
                return True
        return False
    
    def get_plausible_patches(self, mode=None):
        plausible_patches = []
        if mode is None:
            for p in self.proposed_patches:
                if p["test_result"] == "PASS":
                    plausible_patches.append(p)
        else:
            for p in self.proposed_patches:
                if p["test_result"] == "PASS" and p["patch_mode"] == mode:
                    plausible_patches.append(p)
        return plausible_patches
    
    def get_plausible_patch_diffs(self, mode=None):
        plausible_patch_diffs = []
        if mode is None:
            for p in self.proposed_patches:
                if p["test_result"] == "PASS":
                    plausible_patch_diffs.append(p["patch_diff"])
        else:
            for p in self.proposed_patches:
                if p["test_result"] == "PASS" and p["patch_mode"] == mode:
                    plausible_patch_diffs.append(p["patch_diff"])
        return plausible_patch_diffs

    def get_test_failure_count(self):
        count = 0
        for p in self.proposed_patches:
            if p["test_result"] == "FAIL":
                count += 1
        return count
    
    def get_test_error_count(self):
        count = 0
        for p in self.proposed_patches:
            if p["test_result"] == "ERROR":
                count += 1
        return count
    
    def get_call_num_of_first_plausible_patch(self):
        unique_calls = []
        for p in self.proposed_patches:
            unique_calls.append(p["response"]) if p["response"] not in unique_calls else None
            if p["test_result"] == "PASS":
                return len(unique_calls)
        