class ProposedPatch(object):
        
    def __init__(self, response, test_result, result_reason, mode, patch, patch_diff):
        self.response = response
        self.test_result = test_result
        self.result_reason = result_reason
        self.mode = mode
        self.patch = patch
        self.patch_diff = patch_diff

class ProposedPatches(object):
    
    def __init__(self, proposed_patches = None):
        self.proposed_patches = proposed_patches or []

    def add(self, response, test_result, result_reason, mode, patch, patch_diff):
        for p in self.proposed_patches:
            if p.patch == patch and p.mode == mode:
                return

        self.proposed_patches.append(ProposedPatch(response=response, test_result=test_result, result_reason=result_reason, mode=mode, patch=patch, patch_diff=patch_diff))

    def length(self, mode=None):
        if mode is None:
            return len(self.proposed_patches)
        else:
            return len([p for p in self.proposed_patches if p.mode == mode])

    def contains_plausible_patch(self, mode=None):
        if mode is None:
            for p in self.proposed_patches:
                if p.test_result == "PASS":
                    print("asd")
                    return True
        else:
            for p in self.proposed_patches:
                if p.test_result == "PASS" and p.mode == mode:
                    print("asd")
                    return True
        return False
    
    def get_plausible_patches(self, mode=None):
        plausible_patches = []
        if mode is None:
            for p in self.proposed_patches:
                if p.test_result == "PASS":
                    plausible_patches.append(p)
        else:
            for p in self.proposed_patches:
                if p.test_result == "PASS" and p.mode == mode:
                    plausible_patches.append(p)
        return plausible_patches
    
    def get_plausible_patch_diffs(self, mode=None):
        plausible_patch_diffs = []
        if mode is None:
            for p in self.proposed_patches:
                if p.test_result == "PASS":
                    plausible_patch_diffs.append(p.patch_diff)
        else:
            for p in self.proposed_patches:
                if p.test_result == "PASS" and p.mode == mode:
                    plausible_patch_diffs.append(p.patch_diff)
        return plausible_patch_diffs

    def get_test_failure_count(self):
        count = 0
        for p in self.proposed_patches:
            if p.test_result == "FAIL":
                count += 1
        return count
    
    def get_test_error_count(self):
        count = 0
        for p in self.proposed_patches:
            if p.test_result == "ERROR":
                count += 1
        return count
    
    def get_call_num_of_first_plausible_patch(self):
        unique_calls = []
        for p in self.proposed_patches:
            unique_calls.append(p.response) if p.response not in unique_calls else None
            if p.test_result == "PASS":
                return len(unique_calls)
            
    def get_responses(self, mode=None):
        responses = []
        if mode is None:
            for p in self.proposed_patches:
                if p.response not in responses:
                    responses.append(p.response)
        else:
            for p in self.proposed_patches:
                if p.mode == mode and p.response not in responses:
                    responses.append(p.response)
        return responses
    
    def order(self, mode=None):
        if mode is None:
            return sorted(self.proposed_patches.copy(), key=lambda k: (k.test_result != "ERROR", k.test_result != "FAIL", k.test_result != "PASS"))
        else:
            return sorted([p for p in self.proposed_patches if p.mode == mode], key=lambda k: (k.test_result != "ERROR", k.test_result != "FAIL", k.test_result != "PASS"))
    