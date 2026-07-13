"""Modelos de datos del pipeline de extracción."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone


@dataclass
class DomainResult:
    dominio: str
    nombre: str
    requerido: bool
    sub_items: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "dominio": self.dominio,
            "nombre": self.nombre,
            "requerido": self.requerido,
            "sub_items": self.sub_items,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "DomainResult":
        return cls(
            dominio=data["dominio"],
            nombre=data["nombre"],
            requerido=data["requerido"],
            sub_items=list(data.get("sub_items", [])),
        )


@dataclass
class VacancyRecord:
    url: str
    url_normalizada: str
    fecha_extraccion: str
    dominios: list[DomainResult]

    @classmethod
    def create(cls, url: str, url_normalizada: str, dominios: list[DomainResult]) -> "VacancyRecord":
        return cls(
            url=url,
            url_normalizada=url_normalizada,
            fecha_extraccion=datetime.now(timezone.utc).isoformat(),
            dominios=dominios,
        )

    def to_dict(self) -> dict:
        return {
            "url": self.url,
            "url_normalizada": self.url_normalizada,
            "fecha_extraccion": self.fecha_extraccion,
            "dominios": [d.to_dict() for d in self.dominios],
        }

    @classmethod
    def from_dict(cls, data: dict) -> "VacancyRecord":
        return cls(
            url=data["url"],
            url_normalizada=data["url_normalizada"],
            fecha_extraccion=data["fecha_extraccion"],
            dominios=[DomainResult.from_dict(d) for d in data.get("dominios", [])],
        )
