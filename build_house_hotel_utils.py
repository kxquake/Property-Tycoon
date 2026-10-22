# creates the map for colour groups
category_map = {
    "brown_blue": ["Brown", "Blue"],
    "purple_orange": ["Purple", "Orange"],
    "red_yellow": ["Red", "Yellow"],
    "green_deep_blue": ["Green", "Deep blue"]
}


def get_cost_cat_for_group(group_name):
    """
    Get the colour category cost for a property.
    - group_name: The colour category.
    Returns:
        The colour category for the property if there is one.
    """
    for cat, groups in category_map.items():
        if group_name in groups:
            return cat
    return None


def can_build_house(property_name, properties):
    """
    Checks if a player can build a house for a given property
    - property_name: The name of the property
    - properties: The list of properties
    Returns: True if they can. False otherwise.
    """
    prop = next(p for p in properties if p["name"] == property_name)
    group = prop["group"]
    group_props = [p for p in properties if p["group"] == group]
    values = [(p.get("houses", 0) + 1 if p["name"] == property_name else p.get("houses", 0)) for p in group_props]
    # make sure there isnt a difference greater then 1 on properties
    return max(values) - min(values) <= 1


def can_build_hotel(property_name, properties):
    """
    Checks if a player can build hotels for a given property
    - property_name: The name of the property
    - properties: List of properties
    """
    prop = next(p for p in properties if p["name"] == property_name)
    group = prop["group"]
    group_props = [p for p in properties if p["group"] == group]
    # checks that there are already 4 houses on the property
    if prop.get("houses", 0) != 4 or prop.get("hotels", 0) != 0:
        return False
    for p in group_props:
        if p["name"] != property_name:
            if p.get("houses", 0) < 4 and p.get("hotels", 0) == 0:
                return False
    return True


def can_sell_house(name, group_props, player):
    """
    Determines if a house can be sold form a property while maintaining an even distribution of houses
    across the colour group.
    - name: The name of the property
    - group_props: List of all properties in the same colour group
    - player: The player attempting to sell the house
    Returns:
        bool: True if the house can be sold from property, False otherwise
    """

    pending_transactions = {
        "sell_houses": {},
        "sell_hotels": {}
    }
    house_counts = []

    for prop in group_props:
        dev = next((p for p in player.properties if p["name"] == prop["name"]), {})
        base_houses = dev.get("houses", 0)
        pending_houses = pending_transactions["sell_houses"].get(prop["name"], 0)
        pending_hotels = pending_transactions["sell_hotels"].get(prop["name"], 0)

        # Include converted houses from pending hotel sales
        future_count = base_houses + (4 * pending_hotels) - pending_houses

        if prop["name"] == name:
            future_count -= 1  # Simulate removing one house

        house_counts.append(future_count)
    # checks that there isnt a house difference greater than 1 in the properties in a group
    return max(house_counts) - min(house_counts) <= 1
