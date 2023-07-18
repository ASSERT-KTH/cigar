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
    
    def get_plausible_patches(self):
        plausible_patches = []
        for p in self.proposed_patches:
            if p["test_result"] == "PASS":
                plausible_patches.append(p)
        return plausible_patches
    
    def get_plausible_patches(self, mode):
        plausible_patches = []
        for p in self.proposed_patches:
            if p["test_result"] == "PASS" and p["patch_mode"] == mode:
                plausible_patches.append(p)
        return plausible_patches
    
    def get_plausible_patch_diffs(self):
        plausible_patch_diffs = []
        for p in self.proposed_patches:
            if p["test_result"] == "PASS":
                plausible_patch_diffs.append(p["patch_diff"])
        return plausible_patch_diffs
    
    def get_plausible_patch_diffs(self, mode):
        plausible_patch_diffs = []
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
    