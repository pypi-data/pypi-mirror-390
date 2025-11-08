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
Machi Koro 2 Dice rolling testing.
"""
import pytest

from mk2lib.dice import Dice


def test_dice_roll():
    """
    Test rolling a single dice.
    """
    dice = Dice.roll(dual=False)
    assert dice.dice2 is None
    assert dice.dice is not None
    assert dice.dice in range(1, 7)
    assert not dice.dual
    assert dice.sum == dice.dice
    assert not dice.double


def test_dice_dual_roll():
    """
    Test rolling a two dice.
    """
    dice = Dice.roll(dual=True)
    assert dice.dice is not None
    assert dice.dice2 is not None
    assert dice.dice in range(1, 7)
    assert dice.dice2 in range(1, 7)
    assert dice.dual
    assert dice.sum == (dice.dice + dice.dice2)
    assert dice.double == (dice.dice == dice.dice2)


@pytest.mark.parametrize(
    "d1,d2,expected_dual,expected_double,expected_sum",
    [
        (6, None, False, False, 6),
        (6, 5, True, False, 11),
        (6, 6, True, True, 12),
    ],
)
def test_dice_properties(d1, d2, expected_dual, expected_double, expected_sum):
    """
    Check that properties appropriately represent dice state.
    """
    dice = Dice(d1, d2)
    assert dice.dual == expected_dual
    assert dice.double == expected_double
    assert dice.sum == expected_sum
    save = dice.serialize()
    restored_dice = Dice.deserialize(save)
    assert dice == restored_dice
    assert restored_dice.dual == expected_dual
    assert restored_dice.double == expected_double
    assert restored_dice.sum == expected_sum


def test_dice_roll_randomness():
    """
    Check dice range.
    """
    for _ in range(1000):
        dice = Dice.roll(dual=False)
        assert 1 <= dice.dice <= 6
        assert dice.dice2 is None
