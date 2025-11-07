import numpy as np

class BenchmarkFunctions:
    """Standard benchmark optimization functions"""
    
    @staticmethod
    def sphere(x):
        """Sphere function: f(x) = sum(x^2)"""
        return np.sum(x**2)
    
    @staticmethod
    def rastrigin(x):
        """Rastrigin function"""
        A = 10
        n = len(x)
        return A * n + np.sum(x**2 - A * np.cos(2 * np.pi * x))
    
    @staticmethod
    def rosenbrock(x):
        """Rosenbrock function"""
        return np.sum(100 * (x[1:] - x[:-1]**2)**2 + (1 - x[:-1])**2)
    
    @staticmethod
    def ackley(x):
        """Ackley function"""
        a, b, c = 20, 0.2, 2 * np.pi
        n = len(x)
        sum1 = np.sum(x**2)
        sum2 = np.sum(np.cos(c * x))
        return -a * np.exp(-b * np.sqrt(sum1 / n)) - np.exp(sum2 / n) + a + np.exp(1)
    
    @staticmethod
    def griewank(x):
        """Griewank function"""
        sum_part = np.sum(x**2) / 4000
        prod_part = np.prod(np.cos(x / np.sqrt(np.arange(1, len(x) + 1))))
        return sum_part - prod_part + 1
    
    @staticmethod
    def schwefel(x):
        """Schwefel function"""
        n = len(x)
        return 418.9829 * n - np.sum(x * np.sin(np.sqrt(np.abs(x))))
    
    @staticmethod
    def levy(x):
        """Levy function"""
        w = 1 + (x - 1) / 4
        term1 = np.sin(np.pi * w[0])**2
        term3 = (w[-1] - 1)**2 * (1 + np.sin(2 * np.pi * w[-1])**2)
        
        wi = w[:-1]
        sum_term = np.sum((wi - 1)**2 * (1 + 10 * np.sin(np.pi * wi + 1)**2))
        
        return term1 + sum_term + term3

BENCHMARK_FUNCTIONS = {
    'sphere': BenchmarkFunctions.sphere,
    'rastrigin': BenchmarkFunctions.rastrigin,
    'rosenbrock': BenchmarkFunctions.rosenbrock,
    'ackley': BenchmarkFunctions.ackley,
    'griewank': BenchmarkFunctions.griewank,
    'schwefel': BenchmarkFunctions.schwefel,
    'levy': BenchmarkFunctions.levy
}

FUNCTION_BOUNDS = {
    'sphere': (-100, 100),
    'rastrigin': (-5.12, 5.12),
    'rosenbrock': (-2.048, 2.048),
    'ackley': (-32, 32),
    'griewank': (-600, 600),
    'schwefel': (-500, 500),
    'levy': (-10, 10)
}
