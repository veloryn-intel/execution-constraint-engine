def should_block(current_cost, estimated_cost, limit):
    return (current_cost + estimated_cost) >= limit
