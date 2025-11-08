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
Classes for representing Machi Koro 2 Landmark and Establishment cards.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import TYPE_CHECKING

from mk2lib.const import ActivationOrder, LandmarkKind, Kind, Effect

if TYPE_CHECKING:
    from mk2lib.effects import CardEffect
    from mk2lib.game import MachiKoroGame
    from mk2lib.player import Player


@dataclass
class Card(ABC):
    """
    Base card class with common fields.
    """

    name: str  # Enterprise type
    effect: CardEffect  # Effect of this card
    quantity: int  # Number of cards of that type

    @abstractmethod
    def get_real_price(self, game: MachiKoroGame, buyer: Player) -> int | None:
        """
        Calculate real price of this card for buyer & respecting game's active effects.

        This will apply all modifiers and effect rules to the base cost of card.

        :param game: Game for which price is checked. Used to check e.g. effects.
        :param buyer: Player, who wants to buy card. Used to check e.g. landmark count.
        :return: Integer with final cost of card. None if purchase is not possible.
        """
        raise NotImplementedError  # pragma: no cover


@dataclass
class Establishment(Card):
    """Represents an Establishment card in Machi Koro 2."""

    activation_numbers: list[int]  # Numbers that this establishment activate on
    cost: int  # Price of this establishment to build
    category: Kind  # Category of this card
    order: ActivationOrder  # Activation order (color) of this card

    def get_real_price(self, game: MachiKoroGame, buyer: Player) -> int:
        """
        Get real price of this card for buyer.

        For Establishment card, it's always the only price drawn on the card.

        :param game: Game for which price is checked. Used to check e.g. effects.
        :param buyer: Player, who wants to buy card. Used to check e.g. landmark count.
        :return: Integer with final cost of card.
        """
        return self.cost  # Establishment always have one price for everyone


@dataclass
class Landmark(Card):
    """Represents a Landmark card in Machi Koro 2."""

    cost: list[int | None]  # List of prices to buy this card for each landmark count
    is_promo: bool  # Whether this card is a part of promo addon
    kind: LandmarkKind  # Kind (and color) of this landmark

    def get_real_price(self, game: MachiKoroGame, buyer: Player) -> int | None:
        """
        Calculate real price of this card for buyer & respecting game's active effects.

        This will select right price for player's built landmark count, then will
        apply all active discounts. If player is not allowed to buy this card - it
        will return None.

        :param game: Game for which price is checked. Used to check e.g. effects.
        :param buyer: Player, who wants to buy card. Used to check e.g. landmark count.
        :return: Integer with final cost of card. None if purchase is not possible.
        """
        real_price = self.cost[len(buyer.landmarks)]
        if real_price is None:
            return None
        if buyer.have_loan_office:
            real_price -= 2
        if self.name == "launch_pad":
            if Effect.LAUNCH_PAD_DISCOUNT in game.active_effects:
                real_price -= 5
        if self.name == "loan_office":
            if not game.is_player_eligible_for_loan_office(buyer):
                return None
        return real_price
