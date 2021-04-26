class TargetIsInSameWorkspaceAsSourcePolicy:

    @staticmethod
    def is_satisfied_by(source, target):
        def get_workspace(element):
            if hasattr(element, "parent"):
                return element.parent.workspace
            return element.workspace
        return get_workspace(source) == get_workspace(target)
