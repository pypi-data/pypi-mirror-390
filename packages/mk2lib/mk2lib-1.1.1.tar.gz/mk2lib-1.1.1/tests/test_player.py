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
Machi Koro 2 Player class testing.
"""
from dataclasses import replace

import pytest

from mk2lib.player import Player
from mk2lib.const import ActivationOrder, Kind
from mk2lib.mk2deck import DECK_1_6, DECK_LANDMARKS


# --- Fixtures ---
@pytest.fixture
def player():
    """
    Fixture returning player instance for test.
    """
    return Player(player_id=1)


@pytest.fixture
def sample_establishments():
    """
    Give first 3 establishments.
    """
    return DECK_1_6[:3]


@pytest.fixture
def sample_landmarks():
    """
    Give first 3 landmarks.
    """
    return DECK_LANDMARKS[:3]


# --- Tests ---


def test_initial_state(player):
    """
    Check that Player object is initialized into expected state.
    """
    assert player.player_id == 1
    assert player.coins == 5
    assert player.initial_build_turns == 3
    assert not player.exchange_establishments
    assert not player.have_loan_office
    assert not player.give_establishment
    assert not player.extra_turn
    assert not player.earned_coins_this_turn
    assert player.establishments == []
    assert player.landmarks == []


def test_serialize_deserialize(player, sample_establishments, sample_landmarks):
    """
    Check that Player can be appropriately serialized and deserialized.
    """
    player.coins = 12
    player.have_loan_office = True
    player.initial_build_turns = 0
    player.extra_turn = True
    player.exchange_establishments = 1
    player.have_loan_office = True
    player.have_launch_pad = True
    player.give_establishment = True
    player.earned_coins_this_turn = True
    player.establishments = [replace(c, quantity=1) for c in sample_establishments]
    player.landmarks = sample_landmarks[:2]

    data = player.serialize()
    restored = player.deserialize(data)
    assert player == restored


def test_add_establishment(player, sample_establishments):
    """
    Give player an Establishment card.
    """
    card = sample_establishments[0]
    player.add_card(card)
    assert card in player.establishments
    assert len(player.establishments) == 1


def test_add_landmark(player, sample_landmarks):
    """
    Give player a Landmark card.
    """
    lm = sample_landmarks[0]
    player.add_card(lm)
    assert lm in player.landmarks
    assert len(player.landmarks) == 1


def test_add_card_invalid_type(player):
    """
    Try to give player invalid object rather than card.
    """
    with pytest.raises(TypeError):
        player.add_card("Not a card")  # invalid type


def test_count_cards_by_category(player, sample_establishments):
    """
    Check that count_cards_by_category appropriately counts establishments.
    """
    player.add_card(sample_establishments[0])
    for card in sample_establishments:
        player.add_card(card)
    assert player.count_cards_by_category(Kind.AGRICULTURE) == 2
    assert player.count_cards_by_category(Kind.FOOD) == 1
    assert player.count_cards_by_category(Kind.MAJOR) == 1
    assert player.count_cards_by_category("nonexistent") == 0


def test_get_activated_establishments(player, sample_establishments):
    """
    Check that appropriate establishments activate for different rolls.
    """
    for card in sample_establishments:
        player.add_card(card)

    result = player.get_activated_establishments(2, ActivationOrder.ANY_TURN)
    assert len(result) == 1
    assert result[0].name == "wheat_field"

    result = player.get_activated_establishments(1, ActivationOrder.OTHER_TURN)
    assert len(result) == 1
    assert result[0].name == "sushi_bar"

    result = player.get_activated_establishments(6, ActivationOrder.OWN_TURN_MAJOR)
    assert len(result) == 1
    assert result[0].name == "business_center"

    result = player.get_activated_establishments(5, ActivationOrder.OWN_TURN)
    assert result == []


def test_can_afford(player):
    """
    Check that affordability check appropriately validates player balance.
    """
    assert player.can_afford(5)
    assert player.can_afford(4)
    assert not player.can_afford(6)
    assert not player.can_afford(None)


def test_take_coins(player):
    """
    Check that take_coins takes valid amounts from player and caps it at 0.
    """
    player.coins = 5
    taken = player.take_coins(3)
    assert taken == 3
    assert player.coins == 2

    taken = player.take_coins(5)  # more than available
    assert taken == 2
    assert player.coins == 0


def test_earn_coins_sets_flag_and_returns_amount(player):
    """
    Check that player can be given coins and earned-coins flag works.
    """
    assert not player.earned_coins_this_turn
    result = player.earn_coins(4)
    assert result == 4
    assert player.coins == 9
    assert player.earned_coins_this_turn


def test_spend_coins_success_and_failure(player):
    """
    Check that spend coins appropriately takes coins and is no-op if not enough money.
    """
    assert player.spend_coins(3)
    assert player.coins == 2

    assert not player.spend_coins(10)
    assert player.coins == 2  # unchanged


def test_chaining_take_and_earn(player):
    """
    Check that take_coins and earn_coins could be chained together.
    """
    p2 = Player(player_id=2, coins=2)
    earned = player.earn_coins(p2.take_coins(5))
    assert earned == 2
    assert player.coins == 7  # 5 + 2
    assert p2.coins == 0


def test_new_turn_resets_flags(player):
    """
    Check that on turn boundary, turn state flags are reset.
    """
    player.extra_turn = True
    player.earned_coins_this_turn = True
    player.new_turn()
    assert not player.extra_turn
    assert not player.earned_coins_this_turn


def test_end_turn_decrements_build_turns(player):
    """
    Check that on turn end initial build phase counter is decremented.
    """
    starting_turns = player.initial_build_turns
    player.earn_coins(5)
    player.end_turn()
    assert player.initial_build_turns == starting_turns - 1
    assert not player.earned_coins_this_turn
    player.initial_build_turns = 0
    player.end_turn()
    assert player.initial_build_turns == 0


def test_is_player_winner(player, sample_landmarks):
    """
    Check that win condition registers properly.
    """
    assert not player.is_winner()
    player.landmarks = sample_landmarks
    assert player.is_winner()
    player.landmarks = []
    assert not player.is_winner()
    player.have_launch_pad = True
    assert player.is_winner()


def test_has_card_pop_card(player, sample_establishments, sample_landmarks):
    """
    Check that appropriate establishments activate for different rolls.
    """
    assert not player.has_card(sample_establishments[0].name)
    for card in sample_establishments:
        player.add_card(card)
    player.add_card(sample_establishments[0])
    assert player.has_card(sample_establishments[0].name)
    player.pop_card(sample_establishments[0].name)
    assert player.has_card(sample_establishments[0].name)
    player.pop_card(sample_establishments[0].name)
    assert not player.has_card(sample_establishments[0].name)
    player.add_card(sample_landmarks[0])
    assert player.has_card(sample_landmarks[0].name)
    player.pop_card(sample_landmarks[0].name)
    assert not player.has_card(sample_landmarks[0].name)
    with pytest.raises(KeyError):
        player.pop_card(sample_landmarks[0].name)
