#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# mk2lib - Machi Koro 2 Game Engine
# Copyright (C) 2025  Vitaly Ostrosablin
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""
Implementation of single/dual dice.
"""

from __future__ import annotations

from dataclasses import dataclass
from random import randint


@dataclass
class Dice:
    """
    This class is for representing and rolling dice.
    """

    dice: int
    dice2: int | None

    @property
    def double(self) -> bool:
        """
        Whether player has rolled a double (two of the same dice).

        :return: Whether player has rolled a double.
        """
        return self.dual and (self.dice == self.dice2)

    @property
    def dual(self) -> bool:
        """
        Whether player had rolled two dice.

        :return: Whether player has rolled two dice.
        """
        return self.dice2 is not None

    @property
    def sum(self) -> int:
        """
        Sum of the roll on dice.

        :return: Sum of dice (or value of dice, if rolled only one).
        """
        return self.dice + (self.dice2 or 0)

    @staticmethod
    def roll(dual=False):
        """
        Roll (one or two) dice.

        :param dual: Whether to roll two dice.
        """
        return Dice(
            dice=randint(1, 6),
            dice2=randint(1, 6) if dual else None,
        )

    def serialize(self) -> dict:
        """
        Serialize dice object into dict.

        :return: Dict with serialized Dice state.
        """
        return {"dice": self.dice, "dice2": self.dice2}

    @classmethod
    def deserialize(cls, data: dict) -> Dice:
        """
        Deserialize dice object from saved data.

        :param data: Dict with serialized Dice object.
        :return: Restored Dice object.
        """
        dice = cls(
            dice=data["dice"],
            dice2=data["dice2"],
        )
        return dice
