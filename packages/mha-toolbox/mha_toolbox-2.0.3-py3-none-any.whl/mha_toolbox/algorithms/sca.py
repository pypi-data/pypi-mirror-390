import numpy as np
import time
from sklearn.neighbors import KNeighborsClassifier
from sklearn.model_selection import train_test_split
from mha_toolbox.base import BaseOptimizer

class SineCosinAlgorithm(BaseOptimizer):
    """
    Sine Cosine Algorithm (SCA) implementation.
    
    SCA is a population-based metaheuristic optimization algorithm that uses
    sine and cosine functions to explore and exploit the search space.
    
    Parameters
    ----------
    a : float, optional
        The constant that controls the balance between exploration and exploitation,
        default=2.0
    lower_bound : float or numpy.ndarray, optional
        Lower boundary constraint. If None, will be determined from data.
    upper_bound : float or numpy.ndarray, optional
        Upper boundary constraint. If None, will be determined from data.
    dimensions : int, optional
        Number of dimensions in the search space. If None, will be determined from data.
    population_size : int, optional
        Size of the population (number of search agents), default=30
    max_iterations : int, optional
        Maximum number of iterations. If None, will be calculated based on dimensions.
    verbose : bool, optional
        Whether to display progress information, default=False
        
    References
    ----------
    Mirjalili, S. (2016). SCA: a sine cosine algorithm for solving optimization problems.
    Knowledge-Based Systems, 96, 120-133.
    """
    
    def __init__(self, *args, a=2.0, **kwargs):
        """
        Initialize the Sine Cosine Algorithm.
        
        Supports flexible initialization:
        - SCA(15, 100) -> population_size=15, max_iterations=100
        - SCA(population_size=15, max_iterations=100)
        
        Parameters
        ----------
        *args : tuple
            Positional arguments: population_size, max_iterations, dimensions
        a : float, optional
            The constant that controls the balance between exploration and exploitation,
            default=2.0
        **kwargs : dict
            Additional parameters passed to the BaseOptimizer
        """
        super().__init__(*args, **kwargs)
        self.a = a
        self.algorithm_name = "SineCosinAlgorithm"
    
    def _optimize(self, objective_function, X=None, y=None, **kwargs):
        if X is not None:
            self.dimensions_ = X.shape[1]
            self.lower_bound_ = np.zeros(self.dimensions_)
            self.upper_bound_ = np.ones(self.dimensions_)
        else:
            if not hasattr(self, 'dimensions_') or self.dimensions_ is None:
                self.dimensions_ = kwargs.get('dimensions', 10)
            if not hasattr(self, 'lower_bound_') or self.lower_bound_ is None:
                lb = kwargs.get('lower_bound', kwargs.get('lb', -10.0))
                self.lower_bound_ = np.full(self.dimensions_, lb) if np.isscalar(lb) else np.array(lb)
            if not hasattr(self, 'upper_bound_') or self.upper_bound_ is None:
                ub = kwargs.get('upper_bound', kwargs.get('ub', 10.0))
                self.upper_bound_ = np.full(self.dimensions_, ub) if np.isscalar(ub) else np.array(ub)
        positions = np.random.uniform(
            low=self.lower_bound_, 
            high=self.upper_bound_, 
            size=(self.population_size_, self.dimensions_)
        )
        best_solution = np.zeros(self.dimensions_)
        best_fitness = float('inf')
        global_fitness = []
        local_fitness = []
        local_positions = []
        for t in range(self.max_iterations_):
            fitnesses = []
            positions_snapshot = []
            for i in range(self.population_size_):
                fitness = objective_function(positions[i, :])
                fitnesses.append(fitness)
                positions_snapshot.append(positions[i, :].copy())
                if fitness < best_fitness:
                    best_fitness = fitness
                    best_solution = positions[i, :].copy()
            r1 = self.a - t * (self.a / self.max_iterations_)
            for i in range(self.population_size_):
                for j in range(self.dimensions_):
                    r2 = (2 * np.pi) * np.random.rand()
                    r3 = 2 * np.random.rand()
                    r4 = np.random.rand()
                    if r4 < 0.5:
                        positions[i, j] += (r1 * np.sin(r2) * abs(r3 * best_solution[j] - positions[i, j]))
                    else:
                        positions[i, j] += (r1 * np.cos(r2) * abs(r3 * best_solution[j] - positions[i, j]))
            positions = np.clip(positions, self.lower_bound_, self.upper_bound_)
            global_fitness.append(best_fitness)
            local_fitness.append(fitnesses)
            local_positions.append(positions_snapshot)
        return best_solution, best_fitness, global_fitness, local_fitness, local_positions


# Provide a function-based interface for backward compatibility
def run(X=None, y=None, objective_func=None, **kwargs):
    """
    Run the Sine Cosine Algorithm optimization.
    
    This function maintains backward compatibility with previous versions
    by providing a functional interface to the SCA class.
    
    Parameters
    ----------
    X : numpy.ndarray, optional
        Input data (features) for feature selection
    y : numpy.ndarray, optional
        Target values for feature selection
    objective_func : callable, optional
        The function to optimize (required if X and y are not provided)
    **kwargs : dict
        Additional parameters to pass to the optimizer
        
    Returns
    -------
    OptimizationModel
        Model containing all results and parameters
    """
    # Create SCA optimizer with provided parameters
    optimizer = SineCosinAlgorithm(
        lower_bound=kwargs.get('lb', None),
        upper_bound=kwargs.get('ub', None),
        dimensions=kwargs.get('dim', None),
        population_size=kwargs.get('pop_size', 30),
        max_iterations=kwargs.get('max_iter', None),
        verbose=kwargs.get('verbose', False)
    )
    
    # Run optimization and return the model
    return optimizer.optimize(X=X, y=y, objective_function=objective_func)

    
    params = {
        'pop_size': kwargs.get('pop_size', 30),  
        'max_iter': kwargs.get('max_iter', max(100, 10 * dim)),  
        'verbose': kwargs.get('verbose', True)
    }

    if X is not None and y is not None:
        print("Running SCA in Feature Selection mode.")
        
        params['dim'] = X.shape[1]
        params['lb'] = kwargs.get('lb', 0)
        params['ub'] = kwargs.get('ub', 1)

        def fs_objective_func(solution):
            selected_features = np.where(solution > 0.5)[0]
            
            if len(selected_features) == 0:
                return 1.0

            X_subset = X[:, selected_features]
            
            X_train, X_test, y_train, y_test = train_test_split(X_subset, y, test_size=0.3, stratify=y, random_state=42)
            
            knn = KNeighborsClassifier(n_neighbors=5)
            knn.fit(X_train, y_train)
            accuracy = knn.score(X_test, y_test)
            
            error_rate = 1 - accuracy
            return error_rate

        params['objective_func'] = fs_objective_func

    elif objective_func is not None:
        print("Running SCA in Benchmark Optimization mode.")
        
        if 'dim' not in kwargs or 'lb' not in kwargs or 'ub' not in kwargs:
            raise ValueError("For benchmark optimization, 'dim', 'lb', and 'ub' must be provided.")
        
        params['dim'] = kwargs.get('dim')
        params['lb'] = kwargs.get('lb')
        params['ub'] = kwargs.get('ub')
        params['objective_func'] = objective_func
    
    else:
        raise ValueError("You must provide either (X, y) for feature selection or an 'objective_func' for optimization.")

    model = _sca_internal(**params)

    model.update({
        'dim': params['dim'],
        'lb': params['lb'],
        'ub': params['ub'],
        'pop_size': params['pop_size'],
        'max_iter': params['max_iter']
    })
    
    return model