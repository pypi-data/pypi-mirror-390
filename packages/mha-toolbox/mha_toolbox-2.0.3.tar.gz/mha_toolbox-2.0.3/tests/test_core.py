"""
Unit Tests for MHA Toolbox Core Functionality
==============================================
Tests validation, optimization, and result handling.
"""

import unittest
import numpy as np
import warnings
from mha_toolbox import optimize, MHAToolbox
from mha_toolbox.validators import OptimizationValidator, validate_optimization_inputs
from mha_toolbox.parallel_optimizer import ParallelOptimizer


class TestValidators(unittest.TestCase):
    """Test input validation functionality."""
    
    def setUp(self):
        self.validator = OptimizationValidator()
    
    def test_validate_bounds_tuple(self):
        """Test tuple bounds validation."""
        lb, ub = self.validator.validate_bounds((-10, 10), dimensions=5)
        self.assertEqual(len(lb), 5)
        self.assertEqual(len(ub), 5)
        self.assertTrue(np.all(lb < ub))
    
    def test_validate_bounds_invalid(self):
        """Test invalid bounds detection."""
        with self.assertRaises(ValueError):
            self.validator.validate_bounds((10, -10), dimensions=5)
    
    def test_validate_dataset(self):
        """Test dataset validation."""
        X = np.random.rand(100, 10)
        y = np.random.randint(0, 2, 100)
        
        self.assertTrue(self.validator.validate_dataset(X, y))
    
    def test_validate_dataset_mismatched_samples(self):
        """Test detection of mismatched sample counts."""
        X = np.random.rand(100, 10)
        y = np.random.randint(0, 2, 50)  # Wrong size
        
        with self.assertRaises(ValueError):
            self.validator.validate_dataset(X, y)
    
    def test_validate_dataset_nan(self):
        """Test detection of NaN values."""
        X = np.random.rand(100, 10)
        X[0, 0] = np.nan
        y = np.random.randint(0, 2, 100)
        
        with self.assertRaises(ValueError):
            self.validator.validate_dataset(X, y)
    
    def test_validate_population_size(self):
        """Test population size validation."""
        pop_size = self.validator.validate_population_size(50, dimensions=10)
        self.assertEqual(pop_size, 50)
    
    def test_validate_iterations(self):
        """Test iteration count validation."""
        iters = self.validator.validate_iterations(100)
        self.assertEqual(iters, 100)
    
    def test_validate_objective_function(self):
        """Test objective function validation."""
        def sphere(x):
            return np.sum(x**2)
        
        self.assertTrue(self.validator.validate_objective_function(sphere))
    
    def test_validate_objective_function_invalid(self):
        """Test detection of invalid objective function."""
        def bad_func(x):
            return "not a number"
        
        with self.assertRaises(ValueError):
            self.validator.validate_objective_function(bad_func)


class TestOptimization(unittest.TestCase):
    """Test core optimization functionality."""
    
    def test_simple_function_optimization(self):
        """Test basic function optimization."""
        def sphere(x):
            return np.sum(x**2)
        
        result = optimize(
            'PSO',
            objective_function=sphere,
            bounds=(-10, 10),
            dimensions=5,
            population_size=20,
            max_iterations=30
        )
        
        self.assertIsNotNone(result.best_fitness_)
        self.assertLess(result.best_fitness_, 10.0)  # Should find good solution
        self.assertEqual(len(result.best_solution_), 5)
        self.assertGreater(result.execution_time_, 0)
    
    def test_feature_selection(self):
        """Test feature selection functionality."""
        from sklearn.datasets import load_iris
        X, y = load_iris(return_X_y=True)
        
        result = optimize(
            'GWO',
            X=X, y=y,
            population_size=20,
            max_iterations=20
        )
        
        self.assertIsNotNone(result.best_fitness_)
        self.assertGreaterEqual(result.best_fitness_, 0)
        self.assertLessEqual(result.best_fitness_, 1)
        self.assertEqual(len(result.best_solution_), X.shape[1])
    
    def test_convergence_tracking(self):
        """Test convergence curve tracking."""
        def sphere(x):
            return np.sum(x**2)
        
        result = optimize(
            'PSO',
            objective_function=sphere,
            bounds=(-10, 10),
            dimensions=5,
            max_iterations=50
        )
        
        self.assertEqual(len(result.global_fitness_), 50)
        # Fitness should improve or stay same (minimization)
        self.assertLessEqual(result.global_fitness_[-1], result.global_fitness_[0])
    
    def test_different_algorithms(self):
        """Test multiple algorithms work correctly."""
        def sphere(x):
            return np.sum(x**2)
        
        algorithms = ['PSO', 'GWO', 'WOA']
        
        for alg in algorithms:
            with self.subTest(algorithm=alg):
                result = optimize(
                    alg,
                    objective_function=sphere,
                    bounds=(-5, 5),
                    dimensions=3,
                    population_size=15,
                    max_iterations=20
                )
                
                self.assertIsNotNone(result.best_fitness_)
                self.assertEqual(result.algorithm_name_, 
                               'ParticleSwarmOptimization' if alg == 'PSO' 
                               else 'GreyWolfOptimizer' if alg == 'GWO'
                               else 'WhaleOptimizationAlgorithm')
    
    def test_hybrid_algorithms(self):
        """Test hybrid algorithms."""
        def sphere(x):
            return np.sum(x**2)
        
        result = optimize(
            'AMSHA',
            objective_function=sphere,
            bounds=(-10, 10),
            dimensions=5,
            max_iterations=30
        )
        
        self.assertIsNotNone(result.best_fitness_)
        self.assertEqual(len(result.best_solution_), 5)


class TestResultObject(unittest.TestCase):
    """Test OptimizationModel result object."""
    
    def test_result_attributes(self):
        """Test result object has all required attributes."""
        def sphere(x):
            return np.sum(x**2)
        
        result = optimize(
            'PSO',
            objective_function=sphere,
            bounds=(-5, 5),
            dimensions=5,
            max_iterations=20
        )
        
        # Check required attributes
        self.assertTrue(hasattr(result, 'best_fitness_'))
        self.assertTrue(hasattr(result, 'best_solution_'))
        self.assertTrue(hasattr(result, 'execution_time_'))
        self.assertTrue(hasattr(result, 'global_fitness_'))
        self.assertTrue(hasattr(result, 'algorithm_name_'))
        self.assertTrue(hasattr(result, 'error_log_'))
        self.assertTrue(hasattr(result, 'warnings_'))
    
    def test_result_is_successful(self):
        """Test success validation."""
        def sphere(x):
            return np.sum(x**2)
        
        result = optimize(
            'PSO',
            objective_function=sphere,
            bounds=(-5, 5),
            dimensions=3,
            max_iterations=20
        )
        
        self.assertTrue(result.is_successful())
    
    def test_convergence_quality(self):
        """Test convergence quality assessment."""
        def sphere(x):
            return np.sum(x**2)
        
        result = optimize(
            'PSO',
            objective_function=sphere,
            bounds=(-10, 10),
            dimensions=5,
            max_iterations=50
        )
        
        quality = result.get_convergence_quality()
        
        self.assertIn('quality', quality)
        self.assertIn('improvement', quality)
        self.assertIn('improvement_pct', quality)
        self.assertGreaterEqual(quality['improvement'], 0)


class TestParallelOptimizer(unittest.TestCase):
    """Test parallel optimization functionality."""
    
    def test_parallel_multiple_runs(self):
        """Test running same algorithm multiple times."""
        def sphere(x):
            return np.sum(x**2)
        
        optimizer = ParallelOptimizer(n_jobs=2)
        
        results = optimizer.run_multiple(
            'PSO',
            n_runs=3,
            objective_function=sphere,
            bounds=(-5, 5),
            dimensions=3,
            population_size=10,
            max_iterations=10
        )
        
        self.assertEqual(len(results['results']), 3)
        self.assertIn('best_result', results)
        self.assertIn('statistics', results)
        self.assertIn('mean_fitness', results['statistics'])
    
    def test_parallel_compare_algorithms(self):
        """Test parallel algorithm comparison."""
        def sphere(x):
            return np.sum(x**2)
        
        optimizer = ParallelOptimizer(n_jobs=2)
        
        comparison = optimizer.compare_algorithms(
            ['PSO', 'GWO'],
            objective_function=sphere,
            bounds=(-5, 5),
            dimensions=3,
            population_size=10,
            max_iterations=10
        )
        
        self.assertIn('ranking', comparison)
        self.assertIn('best_algorithm', comparison)
        self.assertGreater(len(comparison['ranking']), 0)


class TestToolbox(unittest.TestCase):
    """Test MHAToolbox class."""
    
    def test_toolbox_initialization(self):
        """Test toolbox initializes correctly."""
        toolbox = MHAToolbox(verbose=False)
        
        self.assertGreater(len(toolbox.algorithms), 0)
        self.assertIsInstance(toolbox.algorithms, dict)
    
    def test_list_algorithms(self):
        """Test listing algorithms."""
        toolbox = MHAToolbox(verbose=False)
        algorithms = toolbox.list_algorithms()
        
        self.assertIsInstance(algorithms, list)
        self.assertGreater(len(algorithms), 100)  # Should have 100+ algorithms
    
    def test_get_algorithm(self):
        """Test getting specific algorithm."""
        toolbox = MHAToolbox(verbose=False)
        
        # Test with full name
        pso_class = toolbox.get_algorithm('ParticleSwarmOptimization')
        self.assertIsNotNone(pso_class)
        
        # Test with alias
        pso_class_alias = toolbox.get_algorithm('PSO')
        self.assertIsNotNone(pso_class_alias)


def run_tests(verbosity=2):
    """Run all unit tests."""
    # Suppress warnings during tests
    warnings.filterwarnings('ignore')
    
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add all test classes
    suite.addTests(loader.loadTestsFromTestCase(TestValidators))
    suite.addTests(loader.loadTestsFromTestCase(TestOptimization))
    suite.addTests(loader.loadTestsFromTestCase(TestResultObject))
    suite.addTests(loader.loadTestsFromTestCase(TestParallelOptimizer))
    suite.addTests(loader.loadTestsFromTestCase(TestToolbox))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=verbosity)
    result = runner.run(suite)
    
    # Print summary
    print("\n" + "="*70)
    print("📊 TEST SUMMARY")
    print("="*70)
    print(f"Tests run: {result.testsRun}")
    print(f"Successes: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    
    if result.wasSuccessful():
        print("\n✅ All tests passed!")
    else:
        print("\n❌ Some tests failed!")
    
    return result


if __name__ == '__main__':
    run_tests()
