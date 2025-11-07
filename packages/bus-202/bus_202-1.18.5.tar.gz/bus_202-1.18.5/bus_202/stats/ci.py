def ci(stat, n, sd=None, proportion=False, cl=0.95):
    """Returns confidence interval for a mean or proportion"""
    from scipy import stats
    import math
    
    if not 0 < cl < 1:
        raise ValueError("Confidence level must be between 0 and 1")
    
    alpha = 1 - cl
    tail = alpha / 2
    
    if proportion:
        if not 0 <= stat <= 1:
            raise ValueError("Proportion must be between 0 and 1")
        
        se = math.sqrt((stat * (1 - stat)) / n)
        margin = stats.norm.ppf(1 - tail) * se
        
    else:
        if sd is None:
            raise ValueError("Standard deviation required for means")
        
        if sd < 0:
            raise ValueError("Standard deviation must be non-negative")
            
        df = n - 1
        se = sd / math.sqrt(n)
        margin = stats.t.ppf(1 - tail, df) * se
    
    return [float(round(stat - margin, 3)), float(round(stat + margin, 3))]
