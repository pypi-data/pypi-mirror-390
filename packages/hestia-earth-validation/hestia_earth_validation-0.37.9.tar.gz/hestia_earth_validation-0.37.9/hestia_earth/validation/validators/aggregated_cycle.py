from hestia_earth.utils.model import find_primary_product

from hestia_earth.validation.utils import _filter_list_errors, get_lookup_value


def validate_linked_impactAssessment(cycle: dict, list_key: str = "inputs"):
    """
    Validate inputs `impactAssessment` links

    This validation makes sure that some inputs, mapped by the lookup `aggregationInputTermIds` on the primary product,
    have a corresponding `impactAssessment` linked to them.
    This validation can throw an error in the following cases:
    - no Impact Assessment has been found for this Input;
    - some Impact Assessment exist for the Input, but it has not been verified;
    - the lookup `aggregationInputTermIds` has not been set correctly. Please verify the primary product of the Cycle,
    and make sure the lookup `aggregationInputTermIds` has been set correctly.
    """
    primary_product = find_primary_product(cycle) or {}
    input_term_ids = (
        get_lookup_value(primary_product.get("term"), "aggregationInputTermIds") or ""
    ).split(";")

    def validate(values: tuple):
        index, blank_node = values
        is_aggregation_input = blank_node.get("term", {}).get("@id") in input_term_ids
        linked_id = blank_node.get("impactAssessment", {}).get("@id", "")
        is_valid = all([linked_id, "world" not in linked_id])
        return (
            not is_aggregation_input
            or is_valid
            or {
                "level": "error",
                "dataPath": f".{list_key}[{index}]{'.impactAssessment' if linked_id else ''}",
                "message": "must be linked to a verified country-level Impact Assessment",
                "params": {"expected": blank_node.get("country"), "current": linked_id},
            }
        )

    return (
        _filter_list_errors(map(validate, enumerate(cycle.get(list_key, []))))
        if input_term_ids
        else True
    )
