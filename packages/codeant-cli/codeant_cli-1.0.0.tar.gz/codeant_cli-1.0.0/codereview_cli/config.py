from pydantic import BaseModel, Field
from typing import List, Optional
import yaml
from pathlib import Path


class SeverityGate(BaseModel):
    block_on: List[str] = Field(default_factory=lambda: ["HIGH"])

class Privacy(BaseModel):
    mode: str = "remote"  # remote | local

class Config(BaseModel):
    rules: List[dict] = Field(default_factory=list)
    severity_gate: SeverityGate = SeverityGate()
    privacy: Privacy = Privacy()
    language: List[str] = Field(default_factory=lambda: ["java"])

def load_config(path: str) -> Config:
    p = Path(path)
    if not p.exists():
        # return defaults if no file—MVP-friendly
        return Config()
    data = yaml.safe_load(p.read_text(encoding="utf-8")) or {}
    return Config(**data)