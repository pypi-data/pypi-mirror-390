"""Generador de Utilidades de Layout"""

from typing import List
from kardocss.core.config import KardoCSSConfig


def generate_layout_utilities(config: KardoCSSConfig, prefix: str) -> List[str]:
    """Genera utilidades de layout."""
    utilities = []
    
    utilities.append("/* Layout Utilities */")
    
    # Container
    container_config = config.get("container", {})
    utilities.append(f".{prefix}container {{")
    utilities.append("  width: 100%;")
    if container_config.get("center", True):
        utilities.append("  margin-left: auto;")
        utilities.append("  margin-right: auto;")
    padding = container_config.get("padding", "1rem")
    utilities.append(f"  padding-left: {padding};")
    utilities.append(f"  padding-right: {padding};")
    utilities.append("}")
    
    # Display
    displays = ["block", "inline-block", "inline", "flex", "inline-flex", "grid", "inline-grid", "hidden"]
    for display in displays:
        if display == "hidden":
            utilities.append(f".{prefix}{display} {{ display: none; }}")
        else:
            utilities.append(f".{prefix}{display} {{ display: {display}; }}")
    
    # Flexbox direction
    utilities.append(f".{prefix}flex-row {{ flex-direction: row; }}")
    utilities.append(f".{prefix}flex-row-reverse {{ flex-direction: row-reverse; }}")
    utilities.append(f".{prefix}flex-col {{ flex-direction: column; }}")
    utilities.append(f".{prefix}flex-col-reverse {{ flex-direction: column-reverse; }}")
    
    # Flex wrap
    utilities.append(f".{prefix}flex-wrap {{ flex-wrap: wrap; }}")
    utilities.append(f".{prefix}flex-wrap-reverse {{ flex-wrap: wrap-reverse; }}")
    utilities.append(f".{prefix}flex-nowrap {{ flex-wrap: nowrap; }}")
    
    # Justify content
    utilities.append(f".{prefix}justify-start {{ justify-content: flex-start; }}")
    utilities.append(f".{prefix}justify-end {{ justify-content: flex-end; }}")
    utilities.append(f".{prefix}justify-center {{ justify-content: center; }}")
    utilities.append(f".{prefix}justify-between {{ justify-content: space-between; }}")
    utilities.append(f".{prefix}justify-around {{ justify-content: space-around; }}")
    utilities.append(f".{prefix}justify-evenly {{ justify-content: space-evenly; }}")
    
    # Align items
    utilities.append(f".{prefix}items-start {{ align-items: flex-start; }}")
    utilities.append(f".{prefix}items-end {{ align-items: flex-end; }}")
    utilities.append(f".{prefix}items-center {{ align-items: center; }}")
    utilities.append(f".{prefix}items-baseline {{ align-items: baseline; }}")
    utilities.append(f".{prefix}items-stretch {{ align-items: stretch; }}")
    
    # Align content
    utilities.append(f".{prefix}content-start {{ align-content: flex-start; }}")
    utilities.append(f".{prefix}content-end {{ align-content: flex-end; }}")
    utilities.append(f".{prefix}content-center {{ align-content: center; }}")
    utilities.append(f".{prefix}content-between {{ align-content: space-between; }}")
    utilities.append(f".{prefix}content-around {{ align-content: space-around; }}")
    utilities.append(f".{prefix}content-evenly {{ align-content: space-evenly; }}")
    
    # Align self
    utilities.append(f".{prefix}self-auto {{ align-self: auto; }}")
    utilities.append(f".{prefix}self-start {{ align-self: flex-start; }}")
    utilities.append(f".{prefix}self-end {{ align-self: flex-end; }}")
    utilities.append(f".{prefix}self-center {{ align-self: center; }}")
    utilities.append(f".{prefix}self-stretch {{ align-self: stretch; }}")
    utilities.append(f".{prefix}self-baseline {{ align-self: baseline; }}")
    
    # Flex grow & shrink
    utilities.append(f".{prefix}flex-1 {{ flex: 1 1 0%; }}")
    utilities.append(f".{prefix}flex-auto {{ flex: 1 1 auto; }}")
    utilities.append(f".{prefix}flex-initial {{ flex: 0 1 auto; }}")
    utilities.append(f".{prefix}flex-none {{ flex: none; }}")
    utilities.append(f".{prefix}flex-grow {{ flex-grow: 1; }}")
    utilities.append(f".{prefix}flex-grow-0 {{ flex-grow: 0; }}")
    utilities.append(f".{prefix}flex-shrink {{ flex-shrink: 1; }}")
    utilities.append(f".{prefix}flex-shrink-0 {{ flex-shrink: 0; }}")
    
    # Grid columns
    for i in range(1, 13):
        utilities.append(f".{prefix}grid-cols-{i} {{ grid-template-columns: repeat({i}, minmax(0, 1fr)); }}")
    
    utilities.append(f".{prefix}grid-cols-none {{ grid-template-columns: none; }}")
    
    # Grid rows
    for i in range(1, 7):
        utilities.append(f".{prefix}grid-rows-{i} {{ grid-template-rows: repeat({i}, minmax(0, 1fr)); }}")
    
    utilities.append(f".{prefix}grid-rows-none {{ grid-template-rows: none; }}")
    
    # Grid column span
    for i in range(1, 13):
        utilities.append(f".{prefix}col-span-{i} {{ grid-column: span {i} / span {i}; }}")
    
    utilities.append(f".{prefix}col-span-full {{ grid-column: 1 / -1; }}")
    utilities.append(f".{prefix}col-auto {{ grid-column: auto; }}")
    
    # Grid row span
    for i in range(1, 7):
        utilities.append(f".{prefix}row-span-{i} {{ grid-row: span {i} / span {i}; }}")
    
    utilities.append(f".{prefix}row-span-full {{ grid-row: 1 / -1; }}")
    utilities.append(f".{prefix}row-auto {{ grid-row: auto; }}")
    
    # Gap (para flex y grid)
    spacing = config.get("spacing", {})
    for name, value in spacing.items():
        rem_value = value / 16 if value != 0 else 0
        utilities.append(f".{prefix}gap-{name} {{ gap: {rem_value}rem; }}")
        utilities.append(f".{prefix}gap-x-{name} {{ column-gap: {rem_value}rem; }}")
        utilities.append(f".{prefix}gap-y-{name} {{ row-gap: {rem_value}rem; }}")
    
    # Position
    utilities.append(f".{prefix}static {{ position: static; }}")
    utilities.append(f".{prefix}fixed {{ position: fixed; }}")
    utilities.append(f".{prefix}absolute {{ position: absolute; }}")
    utilities.append(f".{prefix}relative {{ position: relative; }}")
    utilities.append(f".{prefix}sticky {{ position: sticky; }}")
    
    # Top, Right, Bottom, Left
    utilities.append(f".{prefix}inset-0 {{ top: 0; right: 0; bottom: 0; left: 0; }}")
    utilities.append(f".{prefix}inset-auto {{ top: auto; right: auto; bottom: auto; left: auto; }}")
    utilities.append(f".{prefix}top-0 {{ top: 0; }}")
    utilities.append(f".{prefix}right-0 {{ right: 0; }}")
    utilities.append(f".{prefix}bottom-0 {{ bottom: 0; }}")
    utilities.append(f".{prefix}left-0 {{ left: 0; }}")
    utilities.append(f".{prefix}top-auto {{ top: auto; }}")
    utilities.append(f".{prefix}right-auto {{ right: auto; }}")
    utilities.append(f".{prefix}bottom-auto {{ bottom: auto; }}")
    utilities.append(f".{prefix}left-auto {{ left: auto; }}")
    
    # Overflow
    utilities.append(f".{prefix}overflow-auto {{ overflow: auto; }}")
    utilities.append(f".{prefix}overflow-hidden {{ overflow: hidden; }}")
    utilities.append(f".{prefix}overflow-visible {{ overflow: visible; }}")
    utilities.append(f".{prefix}overflow-scroll {{ overflow: scroll; }}")
    utilities.append(f".{prefix}overflow-x-auto {{ overflow-x: auto; }}")
    utilities.append(f".{prefix}overflow-y-auto {{ overflow-y: auto; }}")
    utilities.append(f".{prefix}overflow-x-hidden {{ overflow-x: hidden; }}")
    utilities.append(f".{prefix}overflow-y-hidden {{ overflow-y: hidden; }}")
    utilities.append(f".{prefix}overflow-x-scroll {{ overflow-x: scroll; }}")
    utilities.append(f".{prefix}overflow-y-scroll {{ overflow-y: scroll; }}")
    
    # Visibility
    utilities.append(f".{prefix}visible {{ visibility: visible; }}")
    utilities.append(f".{prefix}invisible {{ visibility: hidden; }}")
    
    utilities.append("")
    return utilities

