# Copyright 2025 Q-CTRL. All rights reserved.
#
# Licensed under the Q-CTRL Terms of service (the "License"). Unauthorized
# copying or use of this file, via any medium, is strictly prohibited.
# Proprietary and confidential. You may not use this file except in compliance
# with the License. You may obtain a copy of the License at
#
#    https://q-ctrl.com/terms
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS. See the
# License for the specific language.


from boulderopalscaleupsdk.common.dtypes import ISO8601DatetimeUTCLike
from boulderopalscaleupsdk.device.controller import (
    QBLOXControllerInfo,
    QuantumMachinesControllerInfo,
)
from boulderopalscaleupsdk.device.defcal import DefCalData
from boulderopalscaleupsdk.device.processor import SuperconductingProcessor
from pydantic import BaseModel
from pydantic.dataclasses import dataclass
from rich.console import Console

DeviceName = str


@dataclass
class Defcal:
    gate: str
    addr: str | tuple[str, ...]
    program: str

    def show(self) -> None:
        console = Console()
        console.is_jupyter = False
        console.print(self.program)


@dataclass
class DeviceData:
    qpu: SuperconductingProcessor
    controller_info: QBLOXControllerInfo | QuantumMachinesControllerInfo
    _defcals: dict[tuple[str, tuple[str, ...]], DefCalData]

    def get_defcal(self, gate: str, addr: str | tuple[str, ...]) -> Defcal:
        """
        Get the defcal for a specific gate and address alias.
        """
        if self._defcals == {}:
            raise ValueError("No defcal data available.")
        _addr = (addr,) if isinstance(addr, str) else tuple(i for i in sorted(addr))
        defcal = self._defcals.get((gate, _addr))
        if defcal is None:
            raise KeyError(f"No defcal data found for gate '{gate}' and address '{_addr}'.")
        return Defcal(gate=gate, addr=_addr, program=defcal.program)


class DeviceSummary(BaseModel):
    id: str
    organization_id: str
    name: str
    provider: str
    updated_at: ISO8601DatetimeUTCLike
    created_at: ISO8601DatetimeUTCLike

    def __str__(self):
        return f'DeviceSummary(name="{self.name}", id="{self.id}")'
