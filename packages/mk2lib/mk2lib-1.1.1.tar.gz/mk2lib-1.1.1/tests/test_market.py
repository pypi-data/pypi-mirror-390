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
Machi Koro 2 Market mechanics testing.
"""

import random
import pytest

from mk2lib.mk2deck import Market
from mk2lib.const import Effect


class DummyPlayer:
    """Minimal stub player for testing Market interactions."""

    def __init__(self, coins=100):
        self._coins = coins
        self.establishments = []
        self.landmarks = []
        self.have_loan_office = False

    def can_afford(self, price: int) -> bool:
        if price is None:
            return False
        return self._coins >= price

    def spend_coins(self, price: int) -> None:
        if not self.can_afford(price):
            raise ValueError("Not enough coins")
        self._coins -= price

    def add_card(self, card):
        self.establishments.append(card)

    def __repr__(self):
        return f"<DummyPlayer coins={self._coins} acquired={[c.name for c in self.establishments]}>"


class DummyGame:
    """Minimal stub game to collect events."""

    def __init__(self):
        self.events = []
        self.active_effects = []
        self.loan_office_ok = False

    def emit_event(self, event):
        self.events.append(event)

    def is_player_eligible_for_loan_office(self, player):
        return self.loan_office_ok


@pytest.fixture(autouse=True)
def seeded_rng():
    """Ensure deterministic shuffle for tests."""
    random.seed(42)


def test_market_initial_deal_and_serialize_deserialize():
    """
    Check that Market can be created, does initial deal and save/load works.
    """
    game = DummyGame()
    market = Market(game)

    assert len(market.dealt_low) == 5
    assert len(market.dealt_high) == 5
    assert len(market.dealt_landmarks) == 5

    # Serialize / deserialize roundtrip should reconstruct same structure
    data = market.serialize()
    restored = Market.deserialize(game, data)

    assert set(market.dealt_low.keys()) == set(restored.dealt_low.keys())
    assert all(
        c.quantity == restored.dealt_low[name].quantity
        for name, c in market.dealt_low.items()
    )
    #
    assert all(a == b for a, b in zip(market.est_low, restored.est_low))


def test_can_build_filters_affordable_cards():
    """
    Check that can_build actually filters cards.
    """
    game = DummyGame()
    market = Market(game)

    rich = DummyPlayer(coins=999)
    poor = DummyPlayer(coins=0)

    affordable_for_rich = market.can_build(rich)
    affordable_for_poor = market.can_build(poor)

    assert affordable_for_rich  # rich can build something
    assert affordable_for_poor == []  # poor can't build anything


def test_build_card_success_and_event():
    """
    Check than card from market can be built.
    """
    game = DummyGame()
    market = Market(game)

    player = DummyPlayer(coins=20)

    # Pick one card from dealt_low
    card_name = next(iter(market.dealt_low.keys()))
    card = market.dealt_low[card_name]

    built = market.build_card(player, card_name)

    assert built is not None
    assert built.name == card_name
    assert any(e.card.name == card_name for e in game.events if hasattr(e, "card"))
    assert any(c.name == card_name for c in player.establishments)


def test_build_card_not_enough_money_triggers_event():
    """
    Check that broke player can't build card.
    """
    game = DummyGame()
    market = Market(game)

    player = DummyPlayer(coins=0)  # cannot afford anything

    card_name = next(iter(market.dealt_low.keys()))
    result = market.build_card(player, card_name)

    assert result is None
    assert any(e.__class__.__name__ == "NotEnoughMoney" for e in game.events)


def test_build_card_unavailable_triggers_event():
    """
    Check that we can't build non-existent card.
    """
    game = DummyGame()
    market = Market(game)

    player = DummyPlayer(coins=10)

    result = market.build_card(player, "nonexistent_card")
    assert result is None
    assert any(e.__class__.__name__ == "CardUnavailable" for e in game.events)


def test_build_all_deck():
    """
    Check that we can drain all cards from deck and nothing breaks.
    """
    game = DummyGame()
    market = Market(game)

    player = DummyPlayer(coins=999)

    while market.est_low:
        # Build cards until we run out of deck
        next_card = market.est_low[-1]
        name = next(iter((market.dealt_low.keys())))
        quantity = market.dealt_low[name].quantity
        assert quantity > 0
        result = market.build_card(player, name)
        assert len(market.dealt_low) == 5
        assert result is not None
        if quantity > 1:
            assert market.dealt_low[name].quantity == (quantity - 1)
        else:
            assert next_card.name in market.dealt_low

    # No undealt cards left - drain remaining cards
    while market.dealt_low:
        name = next(iter((market.dealt_low.keys())))
        prev_len = len(market.dealt_low)
        prev_quantity = market.dealt_low[name].quantity
        assert prev_quantity > 0
        result = market.build_card(player, name)
        assert result is not None
        if prev_quantity > 1:
            assert market.dealt_low[name].quantity == (prev_quantity - 1)
        elif prev_quantity == 1:
            assert name not in market.dealt_low
            assert len(market.dealt_low) == (prev_len - 1)

    assert len(market.est_low) == 0
    assert len(market.dealt_low) == 0


def test_building_loan_office():
    """
    Check that loan office build limitation rule is enforced.
    """
    game = DummyGame()
    market = Market(game)

    wasteplayer = DummyPlayer(coins=999)
    player = DummyPlayer(coins=10)
    poor_player = DummyPlayer(coins=5)

    # Waste cards, until loan office becomes available
    while not any(c.name == "loan_office" for c in market.dealt_landmarks.values()):
        assert market.landmarks
        name = next(iter((market.dealt_landmarks.keys())))
        result = market.build_card(wasteplayer, name)
        assert result is not None

    result = market.build_card(player, "loan_office")
    assert result is None
    assert any(e.__class__.__name__ == "CardUnavailable" for e in game.events)
    assert any(e.prohibited == True for e in game.events if hasattr(e, "prohibited"))

    game.events = []
    game.loan_office_ok = True
    result = market.build_card(poor_player, "loan_office")
    assert result is None
    assert any(e.__class__.__name__ == "NotEnoughMoney" for e in game.events)
    assert not any(e.__class__.__name__ == "CardUnavailable" for e in game.events)

    game.events = []
    result = market.build_card(player, "loan_office")
    assert result is not None
    assert not any(e.__class__.__name__ == "NotEnoughMoney" for e in game.events)
    assert not any(e.__class__.__name__ == "CardUnavailable" for e in game.events)


def test_launch_pad_discount():
    """
    Check that launch pad discount from having observatory works.
    """
    game = DummyGame()
    market = Market(game)

    wasteplayer = DummyPlayer(coins=999)
    player = DummyPlayer(coins=40)

    # Waste cards, until launch pad becomes available
    while not any(c.name == "launch_pad" for c in market.dealt_landmarks.values()):
        assert market.landmarks
        name = next(iter((market.dealt_landmarks.keys())))
        result = market.build_card(wasteplayer, name)
        assert result is not None

    result = market.build_card(player, "launch_pad")
    assert result is None
    assert any(e.__class__.__name__ == "NotEnoughMoney" for e in game.events)

    # Assume observatory was built
    game.events = []
    game.active_effects.append(Effect.LAUNCH_PAD_DISCOUNT)
    result = market.build_card(player, "launch_pad")
    assert result is not None
    assert not any(e.__class__.__name__ == "NotEnoughMoney" for e in game.events)


def test_loan_office_discount():
    """
    Check that having loan office discounts landmarks.
    """
    game = DummyGame()
    market = Market(game)

    card = next(iter((market.dealt_landmarks.values())))
    player = DummyPlayer(coins=card.cost[0] - 2)

    result = market.build_card(player, card.name)
    assert result is None
    assert any(e.__class__.__name__ == "NotEnoughMoney" for e in game.events)

    # Assume player acquired loan office
    game.events = []
    player.have_loan_office = True
    result = market.build_card(player, card.name)
    assert result is not None
    assert not any(e.__class__.__name__ == "NotEnoughMoney" for e in game.events)


def test_stacking_discounts():
    """
    Check that several discounts apply simultaneously.
    """
    game = DummyGame()
    market = Market(game)

    wasteplayer = DummyPlayer(coins=999)
    player = DummyPlayer(coins=38)
    player.have_loan_office = True  # Assume we've built it.

    # Waste cards, until launch pad becomes available
    while not any(c.name == "launch_pad" for c in market.dealt_landmarks.values()):
        assert market.landmarks
        name = next(iter((market.dealt_landmarks.keys())))
        result = market.build_card(wasteplayer, name)
        assert result is not None

    # Loan office discount alone is not enough.
    result = market.build_card(player, "launch_pad")
    assert result is None
    assert any(e.__class__.__name__ == "NotEnoughMoney" for e in game.events)

    # Assume observatory was built
    game.events = []
    game.active_effects.append(Effect.LAUNCH_PAD_DISCOUNT)
    result = market.build_card(player, "launch_pad")
    assert result is not None
    assert not any(e.__class__.__name__ == "NotEnoughMoney" for e in game.events)


def test_progressive_landmark_cost():
    """
    Check that landmark cost goes up with number of built landmarks.
    """
    game = DummyGame()
    game.loan_office_ok = True
    market = Market(game)

    player = DummyPlayer()

    for i in range(3):
        card = next(iter((market.dealt_landmarks.values())))
        player._coins = 0 if not i else card.cost[i - 1]
        result = market.build_card(player, card.name)
        assert result is None
        player._coins = card.cost[i]
        result = market.build_card(player, card.name)
        assert result is not None
        player.landmarks.append(result)


def test_market_use_promo():
    """
    Check promo cards being included/excluded correctly.
    """
    game = DummyGame()
    promo = ["city_hall", "private_club", "renovation_company"]
    market = Market(game, use_promo=False)
    for i in reversed(promo):
        for c in market.landmarks + list(market.dealt_landmarks.values()):
            if c.name == i:
                promo.remove(i)
    assert len(promo) == 3
    market = Market(game, use_promo=True)
    for i in reversed(promo):
        for c in market.landmarks + list(market.dealt_landmarks.values()):
            if c.name == i:
                promo.remove(i)
    assert not promo
