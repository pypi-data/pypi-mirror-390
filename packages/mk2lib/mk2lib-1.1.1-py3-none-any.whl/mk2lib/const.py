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
Constants for Machi Koro 2 bot.
"""

from __future__ import annotations
from enum import StrEnum, auto, IntEnum

# Timing constants
INACTIVITY_TIMEOUT = 1800


class ActivationOrder(StrEnum):
    """
    Activation order (that is, color) of Establishment card.
    """

    OTHER_TURN = "other_turn"
    ANY_TURN = "any_turn"
    OWN_TURN = "own_turn"
    OWN_TURN_MAJOR = "own_turn_major"


class Kind(StrEnum):
    """
    Category (symbol) of Establishment card.
    """

    FOOD = "food"
    SHOP = "shop"
    GEAR = "gear"
    AGRICULTURE = "agriculture"
    FLOWER = "flower"
    FRUIT = "fruit"
    MAJOR = "major"
    COMBO = "combo"


class LandmarkKind(StrEnum):
    """
    Landmark card kind (color).
    """

    ANY_TURN_INFINITE = "any_turn_infinite"
    OWN_TURN_ONCE = "own_turn_once"
    OWN_TURN_INFINITE = "own_turn_infinite"
    OWN_TURN_INSTAWIN = "own_turn_instawin"


class Effect(StrEnum):
    """
    Orange landmark card effects.
    """

    SKIP_BUILD_FOR_5_COINS = auto()
    GET_8_COINS_ON_12_ROLL = auto()
    TAKE_2_COINS_ON_DOUBLE = auto()
    BOOST_ONE_COIN_SHOP = auto()
    BOOST_ONE_COIN_FOOD = auto()
    BOOST_ONE_COIN_GEAR = auto()
    BOOST_ONE_COIN_AGRICULTURE = auto()
    NO_EARN_COMPENSATION_ONE_DICE = auto()
    NO_EARN_COMPENSATION_TWO_DICE = auto()
    EXTRA_TURN_ON_DOUBLE = auto()
    GET_COIN_FOR_EACH_FOOD_IF_ROLLED_6 = auto()
    GIVE_ESTABLISHMENT_ON_DOUBLE = auto()
    LAUNCH_PAD_DISCOUNT = auto()


# Mapping of one coin boost effects.
BOOST_ONE_COIN_EFFECTS: dict[Kind, Effect] = {
    Kind.SHOP: Effect.BOOST_ONE_COIN_SHOP,
    Kind.FOOD: Effect.BOOST_ONE_COIN_FOOD,
    Kind.GEAR: Effect.BOOST_ONE_COIN_GEAR,
    Kind.AGRICULTURE: Effect.BOOST_ONE_COIN_AGRICULTURE,
}


class GameState(IntEnum):
    """
    Enum of game states for state machine.
    """

    NOT_STARTED = auto()
    ON_ROLL = auto()
    ON_BUILD = auto()
    ON_ESTABLISHMENT_EXCHANGE = auto()
    ON_ESTABLISHMENT_GIVE = auto()
    TURN_FINISHED = auto()
    FINISHED = auto()
    CANCELLED = auto()

    @property
    def is_game_active(self) -> bool:
        """
        Check that game is not in lobby and isn't closed.

        :return: Whether game is in progress.
        """
        if self in (GameState.NOT_STARTED, GameState.FINISHED, GameState.CANCELLED):
            return False
        return True

    @property
    def is_game_ended(self) -> bool:
        """
        Check that game is not finished.

        :return: Whether game is in lobby or in progress.
        """
        if self in (GameState.FINISHED, GameState.CANCELLED):
            return True
        return False

    @property
    def is_in_lobby(self) -> bool:
        """
        Check that game is not in progress and not finished/cancelled.

        :return: Whether game is in lobby.
        """
        if self == GameState.NOT_STARTED:
            return True
        return False
