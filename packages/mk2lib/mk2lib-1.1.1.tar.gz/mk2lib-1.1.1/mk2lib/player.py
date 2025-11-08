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
A class for representing Machi Koro 2 player.
"""
from __future__ import annotations

from dataclasses import dataclass, field, replace
from typing import TypeAlias

from mk2lib.cards import Establishment, Landmark
from mk2lib.const import ActivationOrder, Kind
from mk2lib.mk2deck import ALL_CARDS


@dataclass
class Player:
    """
    Class representing a player and their state.
    """

    player_id: int
    coins: int = 5
    initial_build_turns: int = 3
    extra_turn: bool = False
    exchange_establishments: int = 0
    have_loan_office: bool = False
    have_launch_pad: bool = False
    give_establishment: bool = False
    earned_coins_this_turn: bool = False
    establishments: list[Establishment] = field(default_factory=list)
    landmarks: list[Landmark] = field(default_factory=list)

    def get_activated_establishments(
        self, number: int, order: ActivationOrder
    ) -> list[Establishment]:
        """
        Return all activated establishments for specified roll and order/color.

        Sort them by minimal of activation numbers.

        :param number: Sum of rolled dice.
        :param order: Order (color) of cards that would be activated.
        :return: List of establishments activated.
        """
        activated = []
        for card in self.establishments:
            if card.order == order and number in card.activation_numbers:
                activated.append(card)
        return sorted(activated, key=lambda x: min(x.activation_numbers))

    def add_card(self, card: Establishment | Landmark) -> None:
        """
        Give a card to player.

        :param card: Card given to a player.
        :return: None.
        """
        if isinstance(card, Establishment):
            self.establishments.append(card)
        elif isinstance(card, Landmark):
            self.landmarks.append(card)
        else:
            raise TypeError(f"Invalid object passed into add_card: {card!r}")

    def has_card(self, card_name: str, only_establishments: bool = False) -> bool:
        """
        Check if player has a card by name.

        Note that if used with only_establishments == False, it would return landmarks,
        which might be unwanted (e.g. if checking for presence of establishment for
        give/exchange). Make sure this is really what you want to do.

        :param card_name: Name of card to check for.
        :param only_establishments: Check only in establishments.
        :return: Boolean, indicating if player has this card.
        """
        for establishment in self.establishments:
            if establishment.name == card_name:
                return True
        if only_establishments:
            return False
        for landmark in self.landmarks:
            if landmark.name == card_name:
                return True
        return False

    def pop_card(self, card_name: str) -> Establishment | Landmark:
        """
        Pop and return card from player's hand.

        :param card_name: Name of card to take.
        :return: Card, removed from player's hand.
        """
        for idx, establishment in enumerate(self.establishments):
            if establishment.name == card_name:
                return self.establishments.pop(idx)
        for idx, landmark in enumerate(self.landmarks):
            if landmark.name == card_name:
                return self.landmarks.pop(idx)
        raise KeyError(f'Player doesn\'t have card "{card_name}"')

    def count_cards_by_category(self, category: Kind) -> int:
        """
        Helper to count establishments of particular category.

        :param category: Card symbol that's being counted.
        :return: Number of cards with matching category in player's possession.
        """
        return sum(1 for card in self.establishments if card.category == category)

    def can_afford(self, price: int | None) -> bool:
        """
        Check if player can pay a specific price.

        Note that None is assumes player can't afford purchase by rules,
        hence always returns False.

        :param price: How much player has to pay.
        :return: Boolean, indicating whether player has enough money.
        """
        if price is None:
            return False
        return self.coins >= price

    def take_coins(self, amount: int) -> int:
        """
        Take up to amount coins from player and return amount taken.

        :param amount: How many coins should be taken from player.
        :return: How many coins were actually taken.
        """
        amount_taken = min(self.coins, amount)
        self.coins -= amount_taken
        return amount_taken

    def earn_coins(self, amount: int) -> int:
        """
        Give player amount of coins. Returns the amount (to allow chaining
        with take_coins, e.g. `player.earn_coins(other_player.take_coins(N))`)

        This method also sets per-turn flag, indicating player has earned coins.

        :param amount: How many coins to give player.
        :return: How many coins were given (useful for chaining with take_coins).
        """
        self.coins += amount
        self.earned_coins_this_turn = True
        return amount

    def spend_coins(self, amount: int) -> bool:
        """
        Spend coins. Returns, whether purchase was successful.

        :param amount: How many coins player is about to spend.
        :return: Boolean, indicating whether purchase was successful.
        """
        if self.coins >= amount:
            self.coins -= amount
            return True
        return False

    def new_turn(self) -> None:
        """
        Called before player's turn begins. Resets some per-turn flags.

        :return: None.
        """
        self.extra_turn = False
        self.earned_coins_this_turn = False

    def end_turn(self) -> None:
        """
        Called when player's turn ends. Decrements initial build phase
        counter and earning flag.

        :return: None.
        """
        self.earned_coins_this_turn = False
        if self.initial_build_turns > 0:
            self.initial_build_turns -= 1

    def is_winner(self) -> bool:
        """
        Returns when win condition is hit - 3 landmarks or launch pad built.

        :return: Whether player is winner.
        """
        if len(self.landmarks) >= 3 or self.have_launch_pad:
            return True
        return False

    def serialize(self) -> dict:
        """
        Convert player's state into JSON-serializable dict.

        :return: Dict holding current state of Player.
        """
        return {
            "player_id": self.player_id,
            "coins": self.coins,
            "initial_build_turns": self.initial_build_turns,
            "extra_turn": self.extra_turn,
            "exchange_establishments": self.exchange_establishments,
            "have_loan_office": self.have_loan_office,
            "have_launch_pad": self.have_launch_pad,
            "give_establishment": self.give_establishment,
            "earned_coins_this_turn": self.earned_coins_this_turn,
            "establishments": [card.name for card in self.establishments],
            "landmarks": [card.name for card in self.landmarks],
        }

    @classmethod
    def deserialize(cls, data: dict) -> Player:
        """
        Restore player's state from JSON-serializable dict.

        :param data: Dict with serialized Player object.
        :return: Deserialized from saved data Player object.
        """
        player = cls(
            player_id=data["player_id"],
            coins=data["coins"],
            initial_build_turns=data["initial_build_turns"],
            extra_turn=data["extra_turn"],
            exchange_establishments=data["exchange_establishments"],
            have_loan_office=data["have_loan_office"],
            have_launch_pad=data["have_launch_pad"],
            give_establishment=data["give_establishment"],
            earned_coins_this_turn=data["earned_coins_this_turn"],
        )

        for card_name in data["establishments"] + data["landmarks"]:
            player.add_card(replace(ALL_CARDS[card_name], quantity=1))

        return player


# Player type definition - either by reference, ID or implicit current player.
PlayerType: TypeAlias = Player | int | None
