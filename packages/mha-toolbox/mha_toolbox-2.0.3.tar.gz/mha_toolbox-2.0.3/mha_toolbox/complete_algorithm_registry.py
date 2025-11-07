"""
Complete Algorithm Registry - All 130+ Algorithms
=================================================

This module provides a comprehensive registry of ALL available algorithms
including main algorithms, hybrid algorithms, and extended algorithms.

Total Count: 108 main algorithms + 22 hybrid algorithms = 130+ algorithms
"""

import os
import importlib
import inspect
from mha_toolbox.base import BaseOptimizer

class CompleteAlgorithmRegistry:
    """
    Complete registry for discovering and managing all 130+ algorithms.
    """
    
    def __init__(self):
        self.algorithms = {}
        self.aliases = {}
        self.categories = {}
        self.hybrid_algorithms = {}
        
    def discover_all_algorithms(self, verbose=True):
        """
        Discover ALL algorithms from:
        1. mha_toolbox/algorithms/*.py (108 files)
        2. mha_toolbox/algorithms/hybrid/*.py (22 files)
        3. Extended algorithm modules
        """
        
        if verbose:
            print("\n" + "="*70)
            print("🔍 DISCOVERING ALL ALGORITHMS IN MHA TOOLBOX")
            print("="*70)
        
        # Step 1: Discover main algorithms
        main_count = self._discover_main_algorithms(verbose)
        
        # Step 2: Discover hybrid algorithms
        hybrid_count = self._discover_hybrid_algorithms(verbose)
        
        # Step 3: Discover extended algorithms
        extended_count = self._discover_extended_algorithms(verbose)
        
        # Step 4: Create aliases
        self._create_all_aliases(verbose)
        
        total = len(self.algorithms)
        
        if verbose:
            print("\n" + "="*70)
            print(f"✅ DISCOVERY COMPLETE!")
            print(f"📊 Total Algorithms: {total}")
            print(f"   • Main Algorithms: {main_count}")
            print(f"   • Hybrid Algorithms: {hybrid_count}")
            print(f"   • Extended Algorithms: {extended_count}")
            print(f"📝 Total Aliases: {len(self.aliases)}")
            print("="*70 + "\n")
        
        return total
    
    def _discover_main_algorithms(self, verbose=True):
        """Discover all algorithms in mha_toolbox/algorithms/*.py"""
        
        if verbose:
            print("\n📁 Scanning: mha_toolbox/algorithms/*.py")
        
        count = 0
        try:
            import mha_toolbox.algorithms
            algorithms_dir = os.path.dirname(mha_toolbox.algorithms.__file__)
            
            # Get all Python files
            py_files = [f for f in os.listdir(algorithms_dir) 
                       if f.endswith('.py') and not f.startswith('__')]
            
            if verbose:
                print(f"   Found {len(py_files)} algorithm files")
            
            for filename in sorted(py_files):
                module_name = f"mha_toolbox.algorithms.{filename[:-3]}"
                
                try:
                    # Import the module
                    module = importlib.import_module(module_name)
                    
                    # Find all classes that inherit from BaseOptimizer
                    for name, obj in inspect.getmembers(module):
                        if (inspect.isclass(obj) and 
                            issubclass(obj, BaseOptimizer) and 
                            obj is not BaseOptimizer and
                            name not in self.algorithms):
                            
                            self.algorithms[name] = obj
                            count += 1
                            
                            if verbose and count % 10 == 0:
                                print(f"   ✓ Discovered {count} algorithms...")
                                
                except Exception as e:
                    if verbose:
                        print(f"   ⚠ Could not import {filename}: {str(e)[:50]}")
            
            if verbose:
                print(f"   ✅ Main algorithms discovered: {count}")
                
        except Exception as e:
            if verbose:
                print(f"   ❌ Error discovering main algorithms: {e}")
        
        return count
    
    def _discover_hybrid_algorithms(self, verbose=True):
        """Discover all hybrid algorithms in mha_toolbox/algorithms/hybrid/*.py"""
        
        if verbose:
            print("\n📁 Scanning: mha_toolbox/algorithms/hybrid/*.py")
        
        count = 0
        try:
            import mha_toolbox.algorithms.hybrid
            hybrid_dir = os.path.dirname(mha_toolbox.algorithms.hybrid.__file__)
            
            # Get all Python files except __init__.py
            py_files = [f for f in os.listdir(hybrid_dir) 
                       if f.endswith('.py') and f != '__init__.py']
            
            if verbose:
                print(f"   Found {len(py_files)} hybrid algorithm files")
            
            for filename in sorted(py_files):
                module_name = f"mha_toolbox.algorithms.hybrid.{filename[:-3]}"
                
                try:
                    # Import the module
                    module = importlib.import_module(module_name)
                    
                    # Find all classes that inherit from BaseOptimizer
                    for name, obj in inspect.getmembers(module):
                        if (inspect.isclass(obj) and 
                            issubclass(obj, BaseOptimizer) and 
                            obj is not BaseOptimizer and
                            name not in self.algorithms):
                            
                            self.algorithms[name] = obj
                            self.hybrid_algorithms[name] = obj
                            count += 1
                            
                            if verbose:
                                print(f"   ✓ {name}")
                                
                except Exception as e:
                    if verbose:
                        print(f"   ⚠ Could not import {filename}: {str(e)[:50]}")
            
            if verbose:
                print(f"   ✅ Hybrid algorithms discovered: {count}")
                
        except Exception as e:
            if verbose:
                print(f"   ❌ Error discovering hybrid algorithms: {e}")
        
        return count
    
    def _discover_extended_algorithms(self, verbose=True):
        """Discover extended/special algorithms from other modules"""
        
        if verbose:
            print("\n📁 Scanning: Extended algorithm modules")
        
        count = 0
        
        # Try to import from extended modules
        extended_modules = [
            'mha_toolbox.extended_algorithms',
            'mha_toolbox.complete_algorithms',
            'mha_toolbox.mega_algorithms',
            'mha_toolbox.hybrid_algorithms',
        ]
        
        for module_name in extended_modules:
            try:
                module = importlib.import_module(module_name)
                
                # Find all classes that inherit from BaseOptimizer
                for name, obj in inspect.getmembers(module):
                    if (inspect.isclass(obj) and 
                        issubclass(obj, BaseOptimizer) and 
                        obj is not BaseOptimizer and
                        name not in self.algorithms):
                        
                        self.algorithms[name] = obj
                        count += 1
                        
                        if verbose:
                            print(f"   ✓ {name} (from {module_name.split('.')[-1]})")
                            
            except ImportError:
                pass  # Module doesn't exist
            except Exception as e:
                if verbose:
                    print(f"   ⚠ Error in {module_name}: {str(e)[:50]}")
        
        if verbose:
            print(f"   ✅ Extended algorithms discovered: {count}")
        
        return count
    
    def _create_all_aliases(self, verbose=True):
        """Create comprehensive aliases for all algorithms"""
        
        if verbose:
            print("\n📝 Creating algorithm aliases...")
        
        # Common algorithm aliases
        common_aliases = {
            # Evolutionary
            'ga': 'GeneticAlgorithm',
            'de': 'DifferentialEvolution',
            'es': 'EvolutionStrategy',
            'ep': 'EvolutionaryProgramming',
            'gp': 'GeneticProgramming',
            
            # Swarm Intelligence
            'pso': 'ParticleSwarmOptimization',
            'aco': 'AntColonyOptimization',
            'abc': 'ArtificialBeeColony',
            'fa': 'FireflyAlgorithm',
            'ba': 'BatAlgorithm',
            'gwo': 'GreyWolfOptimizer',
            'woa': 'WhaleOptimizationAlgorithm',
            'ssa': 'SalpSwarmAlgorithm',
            'alo': 'AntLionOptimizer',
            
            # Bio-Inspired
            'sma': 'SlimeMouldAlgorithm',
            'hba': 'HoneyBadgerAlgorithm',
            'hgs': 'HungerGamesSearch',
            'dmoa': 'DwarfMongooseOptimizationAlgorithm',
            'gao': 'GazelleOptimizationAlgorithm',
            'fpa': 'FlowerPollinationAlgorithm',
            'foa': 'FruitFlyOptimizationAlgorithm',
            'tso': 'TunnicatSwarmOptimization',
            'mrfo': 'MantaRayForagingOptimization',
            
            # Physics-Based
            'sa': 'SimulatedAnnealing',
            'gsa': 'GravitationalSearchAlgorithm',
            'mvo': 'MultiVerseOptimizer',
            'eo': 'EquilibriumOptimizer',
            'aoa': 'ArithmeticOptimizationAlgorithm',
            'hgso': 'HenryGasSolubilityOptimization',
            'wdo': 'WindDrivenOptimization',
            'wca': 'WaterCycleAlgorithm',
            
            # Human-Based
            'tlbo': 'TeachingLearningBasedOptimization',
            'sos': 'SymbioticOrganismsSearch',
            'lca': 'LeagueChampionshipAlgorithm',
            'lcbo': 'LifeChoiceBasedOptimization',
            'qsa': 'QueenBeeEvolution',
            
            # Advanced
            'sca': 'SineCosinAlgorithm',
            'hho': 'HarrisHawksOptimization',
            'gto': 'GorillaTriopsOptimizer',
            'ao': 'AquilaOptimizer',
            'rsa': 'ReptileSearchAlgorithm',
            'run': 'RUNgeKuttaOptimizer',
            'gco': 'GerminalCenterOptimization',
            
            # Search-Based
            'ts': 'TabuSearch',
            'vns': 'VariableNeighborhoodSearch',
            'hc': 'HillClimbing',
            'gbo': 'GradientBasedOptimizer',
            'cs': 'CuckooSearch',
            
            # Nature-Inspired
            'da': 'DragonflyAlgorithm',
            'msa': 'MothSearchAlgorithm',
            'spider': 'SocialSpiderAlgorithm',
            'kh': 'KrillHerdAlgorithm',
            
            # Others
            'bbo': 'BiogeographyBasedOptimization',
            'ica': 'ImperialistCompetitiveAlgorithm',
            'sfla': 'ShuffledFrogLeapingAlgorithm',
            'fwa': 'FireworksAlgorithm',
            'iwo': 'InvasiveWeedOptimization',
            'hs': 'HarmonySearch',
            'mbo': 'MonarchButterflyOptimization',
            'eho': 'ElephantHerdingOptimization',
            'bfo': 'BacterialForagingOptimization',
            
            # Hybrid Algorithm Aliases (2025)
            'amsha': 'Adaptive_Multi_Strategy_Hybrid',
            'gwo_woa': 'GWO_WOA_Hybrid',
            'pso_sca': 'PSO_SCA_Hybrid',
            'abc_gwo': 'ABC_GWO_Hybrid',
        }
        
        # Add common aliases
        for alias, full_name in common_aliases.items():
            if full_name in self.algorithms:
                self.aliases[alias.lower()] = full_name
        
        # Create automatic abbreviations from class names
        for alg_name in self.algorithms.keys():
            # Create abbreviation from capital letters
            abbr = ''.join([c for c in alg_name if c.isupper()]).lower()
            if abbr and abbr not in self.aliases and len(abbr) >= 2:
                self.aliases[abbr] = alg_name
            
            # Add lowercase version of full name
            self.aliases[alg_name.lower()] = alg_name
            
            # For hybrid algorithms, create underscore version
            if 'Hybrid' in alg_name or '_' in alg_name:
                # Convert CamelCase to snake_case
                import re
                snake = re.sub('([A-Z]+)', r'_\1', alg_name).lower().strip('_')
                self.aliases[snake] = alg_name
        
        if verbose:
            print(f"   ✅ Created {len(self.aliases)} aliases")
    
    def get_algorithm(self, name):
        """
        Get algorithm class by name or alias.
        
        Parameters
        ----------
        name : str
            Algorithm name or alias
            
        Returns
        -------
        class
            Algorithm class
        """
        # Check direct name
        if name in self.algorithms:
            return self.algorithms[name]
        
        # Check alias
        if name.lower() in self.aliases:
            full_name = self.aliases[name.lower()]
            return self.algorithms[full_name]
        
        # Check case-insensitive
        for alg_name in self.algorithms.keys():
            if alg_name.lower() == name.lower():
                return self.algorithms[alg_name]
        
        return None
    
    def list_all_algorithms(self):
        """Return list of all algorithm names"""
        return sorted(self.algorithms.keys())
    
    def list_hybrid_algorithms(self):
        """Return list of hybrid algorithm names"""
        return sorted(self.hybrid_algorithms.keys())
    
    def get_algorithm_by_category(self):
        """Group algorithms by category with comprehensive classification"""
        categories = {
            'Evolutionary': [],
            'Swarm Intelligence': [],
            'Bio-Inspired': [],
            'Physics-Based': [],
            'Human-Based': [],
            'Hybrid': [],
            'Advanced Meta-Heuristics': [],
            'Search-Based': [],
            'Nature-Inspired': [],
            'Mathematical': [],
            'Chemical-Based': [],
            'Game-Based': [],
            'Other': []
        }
        
        # Comprehensive categorization based on algorithm characteristics
        for alg_name in self.algorithms.keys():
            name_lower = alg_name.lower()
            
            # Hybrid Algorithms
            if 'hybrid' in name_lower or '_' in alg_name:
                categories['Hybrid'].append(alg_name)
            
            # Evolutionary Algorithms
            elif any(x in name_lower for x in ['genetic', 'evolution', 'differential']):
                categories['Evolutionary'].append(alg_name)
            
            # Swarm Intelligence (expanded)
            elif any(x in name_lower for x in [
                'particle', 'swarm', 'pso', 'bee', 'ant', 'aco', 'abc',
                'wolf', 'whale', 'bat', 'salp', 'antlion', 'lion',
                'elephant', 'wildebeest', 'tuna', 'sandcat'
            ]):
                categories['Swarm Intelligence'].append(alg_name)
            
            # Bio-Inspired (animals, plants, biology)
            elif any(x in name_lower for x in [
                'slime', 'badger', 'mongoose', 'gazelle', 'armadillo',
                'dragonfly', 'firefly', 'butterfly', 'cuckoo', 'krill',
                'manta', 'sailfish', 'seagull', 'seaglion', 'hyena',
                'coyote', 'kookaburra', 'penguin', 'grasshopper',
                'flower', 'pollination', 'fruit', 'fpa', 'ffo',
                'mole', 'rat', 'biogeography', 'ecosystem'
            ]):
                categories['Bio-Inspired'].append(alg_name)
            
            # Physics-Based (expanded)
            elif any(x in name_lower for x in [
                'simulated', 'annealing', 'gravity', 'gsa', 'equilibrium',
                'multiverse', 'mvo', 'henry', 'gas', 'brownian',
                'water', 'wind', 'wave', 'archimedes', 'runge', 'kutta',
                'nuclear', 'reaction'
            ]):
                categories['Physics-Based'].append(alg_name)
            
            # Human-Based (social, cultural, sports)
            elif any(x in name_lower for x in [
                'teaching', 'tlbo', 'learning', 'league', 'championship',
                'student', 'psychology', 'imperialis', 'culture',
                'life', 'choice', 'ski', 'driver', 'tianji', 'horse',
                'forensic', 'investigation'
            ]):
                categories['Human-Based'].append(alg_name)
            
            # Search-Based (explicit search algorithms)
            elif any(x in name_lower for x in [
                'search', 'tabu', 'ts', 'neighborhood', 'vns', 'climbing',
                'hc', 'harmony', 'hs', 'queuing', 'qsa', 'pathfinder',
                'rescue', 'sar'
            ]):
                categories['Search-Based'].append(alg_name)
            
            # Advanced Meta-Heuristics (modern, recent algorithms)
            elif any(x in name_lower for x in [
                'sine', 'cosin', 'sca', 'harris', 'hawk', 'hho',
                'aquila', 'ao', 'gorilla', 'gto', 'gaining', 'sharing',
                'knowledge', 'gsk', 'hunger', 'games', 'hgs',
                'germinal', 'center', 'gco'
            ]):
                categories['Advanced Meta-Heuristics'].append(alg_name)
            
            # Nature-Inspired (natural phenomena, not animals)
            elif any(x in name_lower for x in [
                'spider', 'moth', 'jellyfish', 'squirrel', 'capuchin'
            ]):
                categories['Nature-Inspired'].append(alg_name)
            
            # Mathematical (optimization methods)
            elif any(x in name_lower for x in [
                'gradient', 'gbo', 'cross', 'entropy', 'cem',
                'weighted', 'mean', 'vectors', 'wmov', 'popmusic'
            ]):
                categories['Mathematical'].append(alg_name)
            
            # Chemical-Based
            elif any(x in name_lower for x in [
                'chemical', 'reaction', 'cro', 'atom', 'aso'
            ]):
                categories['Chemical-Based'].append(alg_name)
            
            # Game-Based
            elif any(x in name_lower for x in [
                'tug', 'war', 'towo', 'chaos', 'game', 'cgo'
            ]):
                categories['Game-Based'].append(alg_name)
            
            # Pandemic/Virus-Based
            elif any(x in name_lower for x in [
                'coronavirus', 'chio', 'virus', 'colony', 'vcs'
            ]):
                if 'Pandemic-Inspired' not in categories:
                    categories['Pandemic-Inspired'] = []
                categories['Pandemic-Inspired'].append(alg_name)
            
            # Marine-Based (separate from swarm if needed)
            elif any(x in name_lower for x in [
                'marine', 'predator', 'mpa'
            ]):
                categories['Bio-Inspired'].append(alg_name)
            
            else:
                categories['Other'].append(alg_name)
        
        # Remove empty categories
        categories = {k: v for k, v in categories.items() if v}
        
        return categories
    
    def print_summary(self):
        """Print a comprehensive summary of all algorithms"""
        print("\n" + "="*70)
        print("📊 COMPLETE ALGORITHM REGISTRY SUMMARY")
        print("="*70)
        
        categories = self.get_algorithm_by_category()
        
        for cat_name, algorithms in sorted(categories.items()):
            if algorithms:
                print(f"\n{cat_name} Algorithms ({len(algorithms)}):")
                for i, alg in enumerate(sorted(algorithms), 1):
                    # Get alias if available
                    alias = None
                    for a, full in self.aliases.items():
                        if full == alg and len(a) <= 5:
                            alias = a
                            break
                    
                    if alias:
                        print(f"  {i:3d}. {alg:45s} [{alias}]")
                    else:
                        print(f"  {i:3d}. {alg}")
        
        print("\n" + "="*70)
        print(f"Total Algorithms: {len(self.algorithms)}")
        print(f"Hybrid Algorithms: {len(self.hybrid_algorithms)}")
        print(f"Total Aliases: {len(self.aliases)}")
        print("="*70 + "\n")


# Create global registry instance
_global_registry = None

def get_global_registry():
    """Get or create the global algorithm registry"""
    global _global_registry
    if _global_registry is None:
        _global_registry = CompleteAlgorithmRegistry()
        _global_registry.discover_all_algorithms(verbose=False)
    return _global_registry

def discover_all_algorithms(verbose=True):
    """
    Discover all 130+ algorithms in the toolbox.
    
    Returns
    -------
    dict
        Dictionary of algorithm name -> algorithm class
    """
    registry = CompleteAlgorithmRegistry()
    registry.discover_all_algorithms(verbose=verbose)
    return registry.algorithms

def list_all_algorithms():
    """
    Get a list of all available algorithm names.
    
    Returns
    -------
    list
        Sorted list of algorithm names
    """
    registry = get_global_registry()
    return registry.list_all_algorithms()

def get_algorithm(name):
    """
    Get an algorithm class by name or alias.
    
    Parameters
    ----------
    name : str
        Algorithm name or alias
        
    Returns
    -------
    class or None
        Algorithm class if found, None otherwise
    """
    registry = get_global_registry()
    return registry.get_algorithm(name)


if __name__ == '__main__':
    # Test the registry
    registry = CompleteAlgorithmRegistry()
    count = registry.discover_all_algorithms(verbose=True)
    registry.print_summary()
    
    print("\n✅ Algorithm discovery test completed!")
    print(f"📊 Total: {count} algorithms discovered")
