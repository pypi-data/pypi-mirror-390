from __future__ import annotations
from typing import Literal, Optional
from pydantic import BaseModel, Field, PositiveInt, conint, confloat


class HBConfigModel(BaseModel):
    """Top-level Bayes Optimization configuration (validated)."""
    budget_evals: PositiveInt = Field(default=100, description='Max number of objective evaluations')
    batch_size: PositiveInt = Field(default=4, description='Parallel suggestions per iteration')
    seed: int = Field(default=0, description='Global RNG seed')
    save_every: PositiveInt = Field(default=10, description='Persist results every N observations')
    deterministic: bool = Field(default=True, description='Try to enforce determinism where possible')

class SurrogateConfig(BaseModel):
    kernel: Literal['Matern32', 'Matern52', 'RBF'] = 'Matern32'
    heteroscedastic: bool = True
    ard: bool = True
    normalize_y: bool = True
    noise_floor: float = Field(default=1e-8, ge=0.0)

class AcquisitionConfig(BaseModel):
    kind: Literal['NoisyEI', 'Thompson'] = 'NoisyEI'
    cost_aware: bool = False
    exploration_jitter: float = Field(default=1e-6, ge=0.0)

class SchedulerConfig(BaseModel):
    mode: Literal['async', 'sync'] = 'async'
    q: PositiveInt = 4

class CVRiskConfig(BaseModel):
    k: PositiveInt = 8
    repeats: PositiveInt = 1
    metric: Literal['mse', 'mae', 'nll', 'acc', 'f1'] = 'mse'
    fixed_splits: bool = True

class LoggingConfig(BaseModel):
    level: Literal['DEBUG', 'INFO', 'WARN', 'ERROR'] = 'INFO'
    jsonl_path: Optional[str] = None
    tensorboard_path: Optional[str] = None

class Defaults(BaseModel):
    opt: HBConfigModel = Field(default_factory=lambda: HBConfigModel())
    surrogate: SurrogateConfig = Field(default_factory=lambda: SurrogateConfig())
    acquisition: AcquisitionConfig = Field(default_factory=lambda: AcquisitionConfig())
    scheduler: SchedulerConfig = Field(default_factory=lambda: SchedulerConfig())
    risk_cv: CVRiskConfig = Field(default_factory=lambda: CVRiskConfig())
    logging: LoggingConfig = Field(default_factory=lambda: LoggingConfig())
