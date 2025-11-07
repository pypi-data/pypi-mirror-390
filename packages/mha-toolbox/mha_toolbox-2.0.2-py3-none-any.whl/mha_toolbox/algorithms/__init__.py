"""
Metaheuristic algorithms package
"""

from .sca import SineCosinAlgorithm
from .pso import ParticleSwarmOptimization
from .ga import GeneticAlgorithm
from .gwo import GreyWolfOptimizer
from .woa import WhaleOptimizationAlgorithm
from .fa import FireflyAlgorithm
from .ba import BatAlgorithm
from .aco import AntColonyOptimization
from .de import DifferentialEvolution
from .alo import AntLionOptimizer
from .csa import CapuchinSearchAlgorithm
from .coa import CoyoteOptimizationAlgorithm
from .mrfo import MantaRayForagingOptimization
from .msa import MothSearchAlgorithm
from .pfa import PathfinderAlgorithm
from .ssa import SalpSwarmAlgorithm
from .spider import SocialSpiderAlgorithm
from .tso import TunaSwarmOptimization
from .sma import SlimeMouldAlgorithm
from .ants import ApproximatedNondeterministicTreeSearch
from .ao import AquilaOptimizer
# New algorithms batch 1
from .vcs import VirusColonySearch
from .chio import CoronavirusHerdImmunityOptimization
from .fbi import ForensicBasedInvestigationOptimization
from .ica import ImperialistCompetitiveAlgorithm
from .qsa import QueuingSearchAlgorithm
from .spbo import StudentPsychologyBasedOptimization
from .aoa import ArchimedesOptimizationAlgorithm
from .eo import EquilibriumOptimizer
# New algorithms batch 2
from .hgso import HenryGasSolubilityOptimization
from .sa import SimulatedAnnealing
from .wdo import WindDrivenOptimization
from .cgo import ChaosGameOptimization
from .gbo import GradientBasedOptimizer
from .innov import WeightedMeanOfVectors
from .wca import WaterCycleAlgorithm
from .vns import VariableNeighborhoodSearch
# New algorithms batch 3 - Bio-inspired
from .dmoa import DwarfMongooseOptimization
from .fpa import FlowerPollinationAlgorithm
from .foa import FruitFlyOptimization
from .gao import GiantArmadilloOptimization
from .hba import HoneyBadgerAlgorithm
from .hgs import HungerGamesSearch

# Hybrid Algorithms - now imported from individual files in hybrid folder
from .hybrid import (
    PSO_GA_Hybrid,
    GWO_PSO_Hybrid,
    DE_PSO_Hybrid,
    GA_SA_Hybrid,
    WOA_GA_Hybrid,
    ABC_DE_Hybrid,
    FA_DE_Hybrid,
    CS_GA_Hybrid,
    ALO_PSO_Hybrid,
    SSA_DE_Hybrid,
    MFO_DE_Hybrid,
    DA_GA_Hybrid,
    FPA_GA_Hybrid,
    HS_DE_Hybrid,
    KH_PSO_Hybrid,
    TS_GA_Hybrid,
    ACO_PSO_Hybrid,
    FA_GA_Hybrid,
    WOA_SMA_Hybrid,
    SMA_DE_Hybrid,
    SA_PSO_Hybrid,
    GWO_DE_Hybrid,
)

from .koa import KookaburraOptimization
from .kh import KrillHerdAlgorithm
from .mpa import MarinePredatorsAlgorithm
from .nmr import NakedMoleRatAlgorithm
from .sfo import SailfishOptimizer
from .scso import SandCatSwarmOptimization
from .as_ant import AntSystem
from .bbo import BiogeographyBasedOptimization
from .sos import SymbioticOrganismsSearch
from .who import WildebeestHerdOptimization as WHO
from .ca import CultureAlgorithm as CA
# New algorithms batch 4 - Additional metaheuristics
from .gsk import GainingSharingKnowledgeAlgorithm as GSK
from .lca import LeagueChampionshipAlgorithm as LCA
from .sar import SearchAndRescueOptimization as SAR
from .lcbo import LifeChoiceBasedOptimization as LCBO
from .ssd import SocialSkiDriverOptimization as SSD
from .thro import TianjiHorseRacingOptimization as THRO
from .aso import AtomSearchOptimization as ASO
from .gbmo import GasesBrownianMotionOptimization as GBMO
from .mvo import MultiVerseOptimizer as MVO
from .two import TugOfWarOptimization as TWO
from .cro import ChemicalReactionOptimization as CRO
from .nro import NuclearReactionOptimization as NRO
from .wwo import WaterWavesOptimization as WWO
from .hc import HillClimbing as HC
from .aeo import ArtificialEcosystemOptimization as AEO
from .pm import POPMUSIC as PM
from .hs import HarmonySearch as HS
from .boa import BaseOptimizationAlgorithm as BOA
from .cem import CrossEntropyMethod
from .run import RungeKuttaOptimizer as RUNAlgorithm
from .gco import GerminalCenterOptimization
from .ts import TabuSearch

__all__ = [
    'SineCosinAlgorithm',
    'ParticleSwarmOptimization', 
    'GeneticAlgorithm',
    'GreyWolfOptimizer',
    'WhaleOptimizationAlgorithm',
    'FireflyAlgorithm',
    'BatAlgorithm',
    'AntColonyOptimization',
    'DifferentialEvolution',
    'AntLionOptimizer',
    'CapuchinSearchAlgorithm',
    'CoyoteOptimizationAlgorithm',
    'MantaRayForagingOptimization',
    'MothSearchAlgorithm',
    'PathfinderAlgorithm',
    'SalpSwarmAlgorithm',
    'SocialSpiderAlgorithm',
    'TunaSwarmOptimization',
    'SlimeMouldAlgorithm',
    'ApproximatedNondeterministicTreeSearch',
    'AquilaOptimizer',
    # New algorithms batch 1
    'VirusColonySearch',
    'CoronavirusHerdImmunityOptimization',
    'ForensicBasedInvestigationOptimization',
    'ImperialistCompetitiveAlgorithm',
    'QueuingSearchAlgorithm',
    'StudentPsychologyBasedOptimization',
    'ArchimedesOptimizationAlgorithm',
    'EquilibriumOptimizer',
    # New algorithms batch 2
    'HenryGasSolubilityOptimization',
    'SimulatedAnnealing',
    'WindDrivenOptimization',
    'ChaosGameOptimization',
    'GradientBasedOptimizer',
    'WeightedMeanOfVectors',
    'WaterCycleAlgorithm',
    'VariableNeighborhoodSearch',
    # New algorithms batch 3 - Bio-inspired
    'DwarfMongooseOptimization',
    'FlowerPollinationAlgorithm',
    'FruitFlyOptimization',
    'GiantArmadilloOptimization',
    'HoneyBadgerAlgorithm',
    'HungerGamesSearch',
    'KookaburraOptimization',
    'KrillHerdAlgorithm',
    'MarinePredatorsAlgorithm',
    'NakedMoleRatAlgorithm',
    'SailfishOptimizer',
    'SandCatSwarmOptimization',
    'AntSystem',
    'BiogeographyBasedOptimization',
    'SymbioticOrganismsSearch',
    'WHO',
    'CA',
    # New algorithms batch 4 - Additional metaheuristics
    'GSK',
    'LCA',
    'SAR',
    'LCBO',
    'SSD',
    'THRO',
    'ASO',
    'GBMO',
    'MVO',
    'TWO',
    'CRO',
    'NRO',
    'WWO',
    'HC',
    'AEO',
    'PM',
    'HS',
    'BOA',
    'CrossEntropyMethod',
    'RUNAlgorithm',
    'GerminalCenterOptimization',
    'TabuSearch',
    # Hybrid Algorithms - from individual files
    'PSO_GA_Hybrid',
    'GWO_PSO_Hybrid',
    'DE_PSO_Hybrid',
    'GA_SA_Hybrid',
    'WOA_GA_Hybrid',
    'ACO_PSO_Hybrid',
    'ABC_DE_Hybrid',
    'FA_DE_Hybrid',
    'CS_GA_Hybrid',
    'ALO_PSO_Hybrid',
    'SSA_DE_Hybrid',
    'MFO_DE_Hybrid',
    'DA_GA_Hybrid',
    'FPA_GA_Hybrid',
    'HS_DE_Hybrid',
    'KH_PSO_Hybrid',
    'TS_GA_Hybrid',
    'FA_GA_Hybrid',
    'WOA_SMA_Hybrid',
    'SMA_DE_Hybrid',
    'SA_PSO_Hybrid',
    'GWO_DE_Hybrid',
]

# Common aliases for convenience
PSO = ParticleSwarmOptimization
GA = GeneticAlgorithm
GWO = GreyWolfOptimizer
WOA = WhaleOptimizationAlgorithm
FA = FireflyAlgorithm
BA = BatAlgorithm
ACO = AntColonyOptimization
DE = DifferentialEvolution
ALO = AntLionOptimizer
SCA = SineCosinAlgorithm
SMA = SlimeMouldAlgorithm
SSA = SalpSwarmAlgorithm
TSO = TunaSwarmOptimization
MRFO = MantaRayForagingOptimization