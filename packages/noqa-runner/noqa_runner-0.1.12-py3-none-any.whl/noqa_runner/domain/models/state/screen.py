from __future__ import annotations

import logging

from pydantic import BaseModel, Field, model_validator
from typing_extensions import Self

logger = logging.getLogger(__name__)


class ActiveElement(BaseModel):
    type: str
    value: str | None = None
    name: str | None = None
    label: str | None = None
    enabled: bool = True
    visible: bool = True
    accessible: bool = True
    x: int
    y: int
    width: int
    height: int
    center_x: int | None = None
    center_y: int | None = None
    scrollable: str | None = None
    source: str | None = None

    @model_validator(mode="after")
    def calculate_center_coordinates(self) -> Self:
        """Calculate center_x and center_y if not provided"""
        if self.center_x is None:
            self.center_x = self.x + self.width // 2
        if self.center_y is None:
            self.center_y = self.y + self.height // 2
        return self

    @classmethod
    def factory(cls, xml_element) -> Self:
        return cls(
            type=xml_element.tag,
            value=xml_element.attrib.get("value"),
            name=xml_element.attrib.get("name"),
            label=xml_element.attrib.get("label"),
            enabled=True if xml_element.attrib.get("enabled") == "true" else False,
            visible=True if xml_element.attrib.get("visible") == "true" else False,
            accessible=(
                True if xml_element.attrib.get("accessible") == "true" else False
            ),
            x=int(xml_element.attrib.get("x")),
            y=int(xml_element.attrib.get("y")),
            width=int(xml_element.attrib.get("width")),
            height=int(xml_element.attrib.get("height")),
            # center_x and center_y will be calculated by validator if not provided
            scrollable=xml_element.attrib.get("scrollable"),
            source=xml_element.attrib.get("source"),
        )

    @property
    def string_description(self) -> str:
        coordinates = f"(x:{self.center_x}, y:{self.center_y})"
        return f"type='{self.type}' label='{self.label}' name='{self.name}' coordinates={coordinates}"

    @property
    def xpath(self) -> str | None:
        if self.label is not None and self.name is not None:
            if self.x is not None and self.y is not None:
                return f"//{self.type}[@label='{self.label}' and @name='{self.name}' and @x='{self.x}' and @y='{self.y}']"
            else:
                return f"//{self.type}[@label='{self.label}' and @name='{self.name}']"
        else:
            return f"//{self.type}[@x='{self.x}' and @y='{self.y}']"


class Screen(BaseModel):
    elements_tree: str | None = Field(default=None)
    screenshot_url: str | None = Field(
        default=None
    )  # Public URL for screenshot retrieval
