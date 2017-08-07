def base_get_direct_src_statuses(statues, status_sides, status):
    """Get statuses that can directly transition to the given status."""
    if status not in statues:
        return ()
    return (status,) + tuple(map(
        lambda side: side[0],
        filter(lambda side: side[1] == status, status_sides)
    ))


def base_get_direct_dst_statuses(statues, status_sides, status):
    """Get statuses that the given status can directly transition to."""
    if status not in statues:
        return ()
    return (status,) + tuple(map(
        lambda side: side[1],
        filter(lambda side: side[0] == status, status_sides)
    ))


def base_is_status_transition_allowed(statues, status_sides,
                                      src_status, dst_status):
    """Check if the transition from "src_status" to "dst_status" is allowed."""
    if src_status not in statues or dst_status not in statues:
        return False
    return src_status == dst_status or any(
        map(lambda side: side[0] == src_status and side[1] == dst_status,
            status_sides)
    )
