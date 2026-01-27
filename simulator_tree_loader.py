# simulator_tree_loader.py
from simulator_tree_v1 import SIM_TREE_V1


def get_sim_tree_v1():
    return SIM_TREE_V1


def pick_root_for_stage(tree: dict, stage_label: str) -> str:
    stage = (stage_label or "").lower()
    for rule in tree.get("roots_by_stage", []):
        matches = [str(m).lower() for m in rule.get("match", [])]
        if matches and all(m in stage for m in matches):
            return rule.get("root_id") or tree.get("default_root_id") or "general_root"
    return tree.get("default_root_id") or "general_root"
