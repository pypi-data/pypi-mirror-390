"""
Algorithm Categories and Registry
==================================

Organized categorization of all MHA algorithms for better user experience.
"""

# Algorithm Categories
ALGORITHM_CATEGORIES = {
    "🧬 Evolutionary Algorithms": {
        "algorithms": ["ga", "de", "es", "ep", "gp"],
        "description": "Evolution-inspired algorithms using selection, crossover, and mutation",
        "best_for": "Complex optimization, scheduling, design problems",
        "difficulty": "beginner"
    },
    
    "🐝 Swarm Intelligence": {
        "algorithms": ["pso", "aco", "abc", "fa", "ba", "gwo", "woa", "ssa", "alo"],
        "description": "Collective behavior of decentralized, self-organized systems",
        "best_for": "Continuous optimization, multi-modal problems",
        "difficulty": "beginner"
    },
    
    "🦅 Bio-Inspired Algorithms": {
        "algorithms": ["sma", "hba", "hgs", "dmoa", "gao", "fpa", "foa", "tso", "mrfo"],
        "description": "Inspired by biological processes and animal behaviors",
        "best_for": "Feature selection, high-dimensional optimization",
        "difficulty": "intermediate"
    },
    
    "🌡️ Physics-Based Algorithms": {
        "algorithms": ["sa", "gbo", "eo", "aoa", "mvo", "hgso", "wdo", "wca"],
        "description": "Based on physical laws and phenomena",
        "best_for": "Engineering design, constrained optimization",
        "difficulty": "intermediate"
    },
    
    "🧠 Human-Based Algorithms": {
        "algorithms": ["tlbo", "spbo", "scho", "ica", "qsa"],
        "description": "Inspired by human social behavior and learning",
        "best_for": "Educational data, social network optimization",
        "difficulty": "intermediate"
    },
    
    "🦠 Pandemic-Inspired Algorithms": {
        "algorithms": ["vcs", "chio"],
        "description": "Based on virus behavior and herd immunity",
        "best_for": "Epidemic modeling, network optimization",
        "difficulty": "advanced"
    },
    
    "🔥 Hybrid Algorithms": {
        "algorithms": [
            "pso_ga_hybrid", "gwo_pso_hybrid", "de_pso_hybrid",
            "sa_pso_hybrid", "woa_ga_hybrid", "woa_sma_hybrid",
            "sma_de_hybrid", "aco_pso_hybrid", "abc_de_hybrid",
            "fa_de_hybrid", "fa_ga_hybrid", "cs_ga_hybrid", 
            "alo_pso_hybrid", "ssa_de_hybrid", "gwo_de_hybrid",
            "hs_de_hybrid", "kh_pso_hybrid", "mfo_de_hybrid",
            "ts_ga_hybrid", "da_ga_hybrid", "fpa_ga_hybrid",
            "geneticsimulatedannealinghybrid"
        ],
        "description": "Combines strengths of multiple algorithms for enhanced performance",
        "best_for": "Complex real-world problems, challenging benchmarks, multi-objective optimization",
        "difficulty": "advanced"
    },
    
    "🎯 Advanced Meta-Heuristics": {
        "algorithms": ["sca", "hho", "gto", "ao", "rsa", "aso", "hba", "run", "gco", "ts"],
        "description": "State-of-the-art recent algorithms",
        "best_for": "Cutting-edge research, challenging benchmarks",
        "difficulty": "advanced"
    },
    
    "🔍 Search-Based Algorithms": {
        "algorithms": ["ts", "vns", "ants", "pfa", "fbi", "csa", "coa"],
        "description": "Strategic search and exploration techniques",
        "best_for": "Combinatorial optimization, path finding",
        "difficulty": "intermediate"
    },
    
    "🌊 Nature-Inspired Algorithms": {
        "algorithms": ["spider", "msa", "cgo", "innov", "nro", "wwo"],
        "description": "Based on natural phenomena and ecosystems",
        "best_for": "Environmental modeling, ecological optimization",
        "difficulty": "intermediate"
    }
}

# Difficulty-based recommendations
BEGINNER_ALGORITHMS = [
    "pso", "ga", "gwo", "de", "woa", "ssa", "fa", "ba", "aco", "abc"
]

INTERMEDIATE_ALGORITHMS = [
    "sca", "alo", "tlbo", "sma", "hba", "eo", "aoa", "mvo", "ts", "vns"
]

ADVANCED_ALGORITHMS = [
    "hho", "gto", "ao", "rsa", "run", "gco", "vcs", "chio",
    "pso_ga_hybrid", "gwo_pso_hybrid", "de_pso_hybrid"
]

# Algorithm metadata
ALGORITHM_INFO = {
    "pso": {
        "name": "Particle Swarm Optimization",
        "year": 1995,
        "author": "Kennedy & Eberhart",
        "complexity": "O(n*m*d)",
        "parameters": ["w", "c1", "c2"],
        "type": "swarm"
    },
    "ga": {
        "name": "Genetic Algorithm",
        "year": 1975,
        "author": "Holland",
        "complexity": "O(n*m*d)",
        "parameters": ["crossover_rate", "mutation_rate"],
        "type": "evolutionary"
    },
    "gwo": {
        "name": "Grey Wolf Optimizer",
        "year": 2014,
        "author": "Mirjalili et al.",
        "complexity": "O(n*m*d)",
        "parameters": ["a"],
        "type": "swarm"
    },
    "de": {
        "name": "Differential Evolution",
        "year": 1997,
        "author": "Storn & Price",
        "complexity": "O(n*m*d)",
        "parameters": ["F", "CR"],
        "type": "evolutionary"
    },
    "sca": {
        "name": "Sine Cosine Algorithm",
        "year": 2016,
        "author": "Mirjalili",
        "complexity": "O(n*m*d)",
        "parameters": ["a"],
        "type": "physics"
    },
    "woa": {
        "name": "Whale Optimization Algorithm",
        "year": 2016,
        "author": "Mirjalili & Lewis",
        "complexity": "O(n*m*d)",
        "parameters": ["a", "b"],
        "type": "bio"
    }
}

# Problem type recommendations
PROBLEM_TYPE_RECOMMENDATIONS = {
    "feature_selection": ["pso", "ga", "gwo", "sca", "woa", "pso_ga_hybrid"],
    "continuous_optimization": ["pso", "de", "gwo", "woa", "sca"],
    "discrete_optimization": ["ga", "aco", "ts", "vns"],
    "constrained_optimization": ["pso", "de", "ga", "ssa_de_hybrid"],
    "multi_objective": ["ga", "pso", "de"],
    "high_dimensional": ["hho", "gto", "sca", "hho_de_hybrid"],
    "multimodal": ["fa", "ba", "cs_ga_hybrid"],
    "engineering_design": ["pso", "ga", "de", "aoa_ga_hybrid"]
}

# Dataset-based recommendations
def recommend_algorithms(dataset_features: dict) -> list:
    """
    Recommend algorithms based on dataset characteristics.
    
    Parameters:
    -----------
    dataset_features : dict
        {
            'n_samples': int,
            'n_features': int,
            'n_classes': int,
            'problem_type': str ('binary', 'multiclass', 'regression'),
            'has_missing': bool,
            'feature_types': list
        }
    
    Returns:
    --------
    list : Recommended algorithms with scores
    """
    recommendations = []
    
    n_features = dataset_features.get('n_features', 0)
    n_samples = dataset_features.get('n_samples', 0)
    n_classes = dataset_features.get('n_classes', 2)
    problem_type = dataset_features.get('problem_type', 'binary')
    
    # High-dimensional datasets
    if n_features > 50:
        recommendations.extend([
            {"algo": "hho", "score": 0.95, "reason": "Excellent for high dimensions"},
            {"algo": "gto", "score": 0.90, "reason": "Good exploration in high dimensions"},
            {"algo": "pso", "score": 0.85, "reason": "Efficient for many features"},
            {"algo": "hho_de_hybrid", "score": 0.88, "reason": "Hybrid power for complex spaces"}
        ])
    
    # Small datasets
    elif n_samples < 100:
        recommendations.extend([
            {"algo": "ga", "score": 0.90, "reason": "Robust for small samples"},
            {"algo": "pso", "score": 0.85, "reason": "Quick convergence"},
            {"algo": "gwo", "score": 0.83, "reason": "Good balance"}
        ])
    
    # Medium datasets
    elif n_samples < 1000:
        recommendations.extend([
            {"algo": "pso", "score": 0.92, "reason": "Standard choice"},
            {"algo": "gwo", "score": 0.90, "reason": "Reliable performance"},
            {"algo": "sca", "score": 0.87, "reason": "Good exploration"},
            {"algo": "pso_ga_hybrid", "score": 0.89, "reason": "Combined strengths"}
        ])
    
    # Large datasets
    else:
        recommendations.extend([
            {"algo": "de", "score": 0.93, "reason": "Efficient for large data"},
            {"algo": "pso", "score": 0.91, "reason": "Fast and reliable"},
            {"algo": "sca", "score": 0.88, "reason": "Good scalability"}
        ])
    
    # Multiclass problems
    if n_classes > 2:
        recommendations.append(
            {"algo": "ga", "score": 0.90, "reason": "Handles multiclass well"}
        )
    
    # Sort by score and return top recommendations
    recommendations.sort(key=lambda x: x['score'], reverse=True)
    return recommendations[:10]


def get_algorithm_category(algo_name: str) -> str:
    """Get the category of an algorithm."""
    for category, info in ALGORITHM_CATEGORIES.items():
        if algo_name.lower() in info["algorithms"]:
            return category
    return "Other"


def get_algorithms_by_difficulty(difficulty: str) -> list:
    """Get algorithms by difficulty level."""
    if difficulty == "beginner":
        return BEGINNER_ALGORITHMS
    elif difficulty == "intermediate":
        return INTERMEDIATE_ALGORITHMS
    elif difficulty == "advanced":
        return ADVANCED_ALGORITHMS
    else:
        return BEGINNER_ALGORITHMS + INTERMEDIATE_ALGORITHMS + ADVANCED_ALGORITHMS
