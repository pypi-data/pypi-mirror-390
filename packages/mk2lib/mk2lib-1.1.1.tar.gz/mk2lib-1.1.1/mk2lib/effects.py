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
Establishment and Landmark card effects implementation module.
"""

from __future__ import annotations

import math
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import TYPE_CHECKING

from .cards import Card, Landmark
from .const import Effect, Kind
from .events import (
    MoneyTaken,
    MoneyEarned,
    GetExtraTurn,
    NewLandmarkEffectActivated,
    CanExchangeEstablishments,
    MoneyDivided,
)

if TYPE_CHECKING:
    from .game import MachiKoroGame
    from .player import Player


class CardEffect(ABC):
    """
    Base card effect class.
    """

    @staticmethod
    def _earn_money(
        game: MachiKoroGame, card: Card, player: Player, amount: int
    ) -> None:
        """
        Helper method to give player some money from bank.

        :param game: Game instance.
        :param card: Card that caused income.
        :param player: Player who gets the money.
        :param amount: Number of coins gained.
        :return: None.
        """
        player.earn_coins(amount)
        game.emit_event(
            MoneyEarned(
                reason=card,
                user=player,
                earned=amount,
            )
        )

    @staticmethod
    def _take_money(
        game: MachiKoroGame,
        card: Card,
        player_from: Player,
        player_to: Player,
        amount: int,
    ) -> None:
        """
        Helper method to transfer coins between players.

        Note that if paying player doesn't have enough money - all their coins
        are claimed (if any). For that reason, event registers both "owed" amount
        (how much we were supposed to take), and "taken" amount, which represents
        the amount that actually was taken from balance. From these two fields
        it's possible to figure out what exactly happened at the time of event.

        :param game: Game instance.
        :param card: Card that caused income.
        :param player_from: Player whose money are taken.
        :param player_to: Player who gets the money.
        :param amount: Number of coins transferred.
        :return: None.
        """
        game.emit_event(
            MoneyTaken(
                reason=card,
                from_user=player_from,
                to_user=player_to,
                owed=amount,
                taken=player_to.earn_coins(player_from.take_coins(amount)),
            )
        )

    @abstractmethod
    def trigger(
        self, game: MachiKoroGame, card: Card, owner: Player, current: Player
    ) -> None:
        """
        Applies card effect when called (game manages the activation conditions).

        :param game: A game instance.
        :param card: Reference to card that has this effect.
        :param owner: Player who owns this card (usually also one who gets effect).
        :param current: Player, whose turn it is now.
        :return: None.
        """
        raise NotImplementedError  # pragma: no cover


@dataclass
class EarnFromBank(CardEffect):
    """
    Earn coins from bank.
    """

    income: int

    def trigger(
        self, game: MachiKoroGame, card: Card, owner: Player, current: Player
    ) -> None:
        amount_gain = self.income + game.get_gain_modifier(card)
        self._earn_money(game, card, owner, amount_gain)


@dataclass
class EarnFromActivePlayer(CardEffect):
    """
    Take money from player, whose turn it is currently and give them to card's owner.
    """

    amount: int

    def trigger(
        self, game: MachiKoroGame, card: Card, owner: Player, current: Player
    ) -> None:
        amount_owed = self.amount + game.get_gain_modifier(card)
        self._take_money(game, card, current, owner, amount_owed)


@dataclass
class EarnFromBankCombo(CardEffect):
    """
    For COMBO cards, gives income, multiplied by number of cards of particular
    category in player's possession.
    """

    category: Kind
    income: int

    def trigger(
        self, game: MachiKoroGame, card: Card, owner: Player, current: Player
    ) -> None:
        amount_gain = self.income * owner.count_cards_by_category(self.category)
        self._earn_money(game, card, owner, amount_gain)


class ExchangeEstablishments(CardEffect):
    """
    Business center's effect. Gives an ability to exchange one of player's
    establishment cards with any establishment of another player.
    """

    def trigger(
        self, game: MachiKoroGame, card: Card, owner: Player, current: Player
    ) -> None:
        owner.exchange_establishments += 1
        game.emit_event(CanExchangeEstablishments(player=owner))


class TakeHalfIfElevenOrMore(CardEffect):
    """
    Take 1/2 coins from any player, who has 11 coins or more and give them to card's
    owner. But amount is rounded down, so that e.g. from player with 11 coins, only
    5 would be taken, not 6.
    """

    def trigger(
        self, game: MachiKoroGame, card: Card, owner: Player, current: Player
    ) -> None:
        for opponent in game.traverse_forward_players(skipcurrent=True):
            if opponent.coins >= 11:
                amount_taken = opponent.coins // 2
                self._take_money(game, card, opponent, owner, amount_taken)


@dataclass
class TakeFromAllOpponents(CardEffect):
    """
    Take specific amount of money from all players and give them to owner.
    """

    amount: int

    def trigger(
        self, game: MachiKoroGame, card: Card, owner: Player, current: Player
    ) -> None:
        for opponent in game.traverse_forward_players(skipcurrent=True):
            self._take_money(game, card, opponent, owner, self.amount)


@dataclass
class TakeCoinForEachEstablishment(CardEffect):
    """
    Take a coin for each opponents' establishment card of particular category.
    """

    category: Kind

    def trigger(
        self, game: MachiKoroGame, card: Card, owner: Player, current: Player
    ) -> None:
        for opponent in game.traverse_forward_players(skipcurrent=True):
            count = opponent.count_cards_by_category(self.category)
            self._take_money(game, card, opponent, owner, count)


@dataclass
class TakeCoinsForEachLandmark(CardEffect):
    """
    Take specific amount of money for each opponents' landmark.
    """

    amount: int

    def trigger(
        self, game: MachiKoroGame, card: Card, owner: Player, current: Player
    ) -> None:
        for opponent in game.traverse_forward_players(skipcurrent=True):
            count = len(opponent.landmarks) * self.amount
            if count:
                self._take_money(game, card, opponent, owner, count)


class TakeFiveCoinsIfTwoLandmarks(CardEffect):
    """
    Private Club's effect. Takes 5 coins from each opponent with 2 landmarks.
    """

    def trigger(
        self, game: MachiKoroGame, card: Card, owner: Player, current: Player
    ) -> None:
        for opponent in game.traverse_forward_players(skipcurrent=True):
            if len(opponent.landmarks) == 2:
                self._take_money(game, card, opponent, owner, 5)


class EvenlyDistributeCoins(CardEffect):
    """
    Collect coins of all players and evenly distribute them among the players.

    NOTE: As per rules, if coins cannot be distributed evenly - extra coins must
    be taken from bank, which means that all players effectively get balance of
    all players' coin average, which is then rounded up (if necessary).
    """

    def trigger(
        self, game: MachiKoroGame, card: Card, owner: Player, current: Player
    ) -> None:
        players = len(game.players)
        total_coins = sum(
            p.take_coins(p.coins) for p in game.traverse_forward_players()
        )
        divided = math.ceil(total_coins / players)  # Rounded up per rulebook
        for player in game.traverse_forward_players():
            player.earn_coins(divided)
        game.emit_event(
            MoneyDivided(
                reason=card,
                players=players,
                total_coins=total_coins,
                from_bank=(divided * players) - total_coins,
                coins=divided,
            )
        )


class ExtraTurn(CardEffect):
    """
    Grant player an extra turn.
    """

    def trigger(
        self, game: MachiKoroGame, card: Card, owner: Player, current: Player
    ) -> None:
        game.emit_event(
            GetExtraTurn(
                player=owner,
                no_effect=owner.extra_turn,
                # If already have extra turn - you don't get another
            )
        )
        owner.extra_turn = True


class InstaWin(CardEffect):
    """
    Launch Pad effect - if you've built it, you instantly win.
    """

    def trigger(
        self, game: MachiKoroGame, card: Card, owner: Player, current: Player
    ) -> None:
        owner.have_launch_pad = True


class BuiltLoanOffice(CardEffect):
    """
    Loan Office effect - adds a loan office flag and notifies that a new
    builder-only effect is now active.
    """

    def trigger(
        self, game: MachiKoroGame, card: Card, owner: Player, current: Player
    ) -> None:
        if isinstance(card, Landmark):
            owner.have_loan_office = True
            game.emit_event(NewLandmarkEffectActivated(card, builder_only=True))


@dataclass
class PersistentEffect(CardEffect):
    """
    Activate a generic ongoing persistent effect of orange landmark cards.
    """

    effect: Effect

    def trigger(
        self, game: MachiKoroGame, card: Card, owner: Player, current: Player
    ) -> None:
        if isinstance(card, Landmark):
            if self.effect not in game.active_effects:
                game.active_effects[self.effect] = card
                game.emit_event(NewLandmarkEffectActivated(card))
