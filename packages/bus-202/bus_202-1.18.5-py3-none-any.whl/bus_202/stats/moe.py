def moe(p=0.5, n=None, cl=0.95):
    """Returns margin of error for a proportion"""
    from scipy import stats
    import math
    
    if n is None:
        raise ValueError("Sample size (n) is required")
    
    if not 0 < cl < 1:
        raise ValueError("Confidence level must be between 0 and 1")
    
    if not 0 <= p <= 1:
        raise ValueError("Proportion must be between 0 and 1")
    
    alpha = 1 - cl
    tail = alpha / 2
    
    se = math.sqrt((p * (1 - p)) / n)
    margin = stats.norm.ppf(1 - tail) * se
    
    return round(margin, 3)
