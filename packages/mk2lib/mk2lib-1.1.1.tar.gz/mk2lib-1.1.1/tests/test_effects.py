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
Machi Koro 2 card effect testing.
"""

import pytest

from mk2lib.cards import Card, Establishment, Landmark
from mk2lib.const import Effect
from mk2lib.game import MachiKoroGame
from mk2lib.mk2deck import DECK_1_6, DECK_7_12, DECK_LANDMARKS


@pytest.fixture
def game_2p():
    """
    Fixture that sets up 2 player game.
    """
    game = MachiKoroGame(1)
    game.join(2)
    _ = game.events.get_nowait()
    _ = game.events.get_nowait()
    return game


@pytest.fixture
def game_4p(game_2p):
    """
    Fixture that sets up 4 player game.
    """
    game_2p.join(3)
    game_2p.join(4)
    _ = game_2p.events.get_nowait()
    _ = game_2p.events.get_nowait()
    return game_2p


def get_card_from_deck(deck: list[Card], name: str) -> Establishment | Landmark | None:
    """
    Get specific card from deck.
    """
    for card in deck:
        if card.name == name:
            return card
    return None


def test_earn_from_bank(game_2p: MachiKoroGame):
    """
    Check that cards that earn money from bank actually give players money.
    """
    card = get_card_from_deck(DECK_1_6, "wheat_field")  # EarnFromBank
    assert game_2p.players[0].coins == 5
    assert game_2p.players[1].coins == 5
    card.effect.trigger(game_2p, card, game_2p.players[1], game_2p.players[0])
    assert game_2p.players[0].coins == 5
    assert game_2p.players[1].coins == 6
    game_2p.active_effects[Effect.BOOST_ONE_COIN_AGRICULTURE] = True
    card.effect.trigger(game_2p, card, game_2p.players[1], game_2p.players[0])
    assert game_2p.players[1].coins == 8
    event = game_2p.events.get_nowait()
    assert event.__class__.__name__ == "MoneyEarned"
    assert event.reason == card
    assert event.user == game_2p.players[1]
    assert event.earned == 1


def test_earn_from_active_player(game_4p: MachiKoroGame):
    """
    Check that FOOD cards actually take money from currently active player.
    """
    card = get_card_from_deck(DECK_1_6, "cafe")  # EarnFromActivePlayer
    game_4p.players[0].coins = 6
    game_4p.players[1].coins = 6
    game_4p.players[2].coins = 1
    game_4p.players[3].coins = 0
    card.effect.trigger(game_4p, card, game_4p.players[1], game_4p.players[0])
    assert game_4p.players[0].coins == 4
    assert game_4p.players[1].coins == 8
    assert game_4p.players[2].coins == 1
    assert game_4p.players[3].coins == 0
    event = game_4p.events.get_nowait()
    assert event.__class__.__name__ == "MoneyTaken"
    assert event.reason == card
    assert event.from_user == game_4p.players[0]
    assert event.to_user == game_4p.players[1]
    assert event.owed == 2
    assert event.taken == 2
    game_4p.active_effects[Effect.BOOST_ONE_COIN_FOOD] = True
    card.effect.trigger(game_4p, card, game_4p.players[1], game_4p.players[0])
    assert game_4p.players[0].coins == 1
    assert game_4p.players[1].coins == 11
    event = game_4p.events.get_nowait()
    assert event.owed == 3
    assert event.taken == 3
    card.effect.trigger(game_4p, card, game_4p.players[1], game_4p.players[2])
    assert game_4p.players[2].coins == 0
    assert game_4p.players[1].coins == 12
    event = game_4p.events.get_nowait()
    assert event.owed == 3
    assert event.taken == 1
    card.effect.trigger(game_4p, card, game_4p.players[1], game_4p.players[3])
    assert game_4p.players[3].coins == 0
    assert game_4p.players[1].coins == 12
    event = game_4p.events.get_nowait()
    assert event.owed == 3
    assert event.taken == 0


def test_earn_from_bank_combo(game_2p: MachiKoroGame):
    """
    Check that COMBO cards correctly account category cards in income calculation.
    """
    card = get_card_from_deck(DECK_1_6, "flower_shop")  # EarnFromBankCombo
    combo_card = get_card_from_deck(DECK_1_6, "flower_garden")
    unrelated_card = get_card_from_deck(DECK_1_6, "vineyard")
    for _ in range(3):
        game_2p.players[1].add_card(combo_card)
        game_2p.players[1].add_card(unrelated_card)
    card.effect.trigger(game_2p, card, game_2p.players[1], game_2p.players[1])
    assert game_2p.players[0].coins == 5
    assert game_2p.players[1].coins == 14
    event = game_2p.events.get_nowait()
    assert event.__class__.__name__ == "MoneyEarned"
    assert event.reason == card
    assert event.user == game_2p.players[1]
    assert event.earned == 9


def test_exchange_establishments(game_2p: MachiKoroGame):
    """
    Check that Business Center increments pending establishment exchange counter.
    """
    card = get_card_from_deck(DECK_1_6, "business_center")  # ExchangeEstablishments
    card.effect.trigger(game_2p, card, game_2p.players[1], game_2p.players[1])
    assert game_2p.players[0].exchange_establishments == 0
    assert game_2p.players[1].exchange_establishments == 1
    event = game_2p.events.get_nowait()
    assert event.__class__.__name__ == "CanExchangeEstablishments"
    assert event.player == game_2p.players[1]


def test_take_half_if_eleven_or_more(game_4p: MachiKoroGame):
    """
    Check that "take half if eleven or more" works and rounding is correct.
    """
    card = get_card_from_deck(DECK_7_12, "shopping_district")  # EarnFromActivePlayer
    game_4p.current_player = 1
    game_4p.players[0].coins = 5
    game_4p.players[1].coins = 12
    game_4p.players[2].coins = 11
    game_4p.players[3].coins = 12
    card.effect.trigger(game_4p, card, game_4p.players[1], game_4p.players[1])
    assert game_4p.players[0].coins == 5
    assert game_4p.players[1].coins == 23
    assert game_4p.players[2].coins == 6
    assert game_4p.players[3].coins == 6
    event = game_4p.events.get_nowait()
    assert event.__class__.__name__ == "MoneyTaken"
    assert event.reason == card
    assert event.from_user == game_4p.players[2]
    assert event.to_user == game_4p.players[1]
    assert event.owed == 5
    assert event.taken == 5


def test_take_from_all_opponents(game_4p: MachiKoroGame):
    """
    Check that "take from opponents" transfers coins from all opponents to owner.
    """
    card = get_card_from_deck(DECK_7_12, "stadium")  # TakeFromAllOpponents
    game_4p.current_player = 1
    card.effect.trigger(game_4p, card, game_4p.players[1], game_4p.players[1])
    # P1 takes 3 from everyone else (9 total)
    assert game_4p.players[1].coins == 14
    assert all(p.coins == 2 for p in game_4p.players if p != game_4p.players[1])
    event = game_4p.events.get_nowait()
    assert event.__class__.__name__ == "MoneyTaken"
    assert event.to_user == game_4p.players[1]
    assert event.from_user == game_4p.players[2]
    assert event.owed == 3


def test_take_coin_for_each_establishment(game_2p: MachiKoroGame):
    """
    Check that calculation of "coin for each card of category" is correct.
    """
    card = get_card_from_deck(
        DECK_LANDMARKS, "publisher"
    )  # TakeCoinForEachEstablishment
    victim_card = get_card_from_deck(DECK_1_6, "convenience_store")
    game_2p.current_player = 1
    for _ in range(3):
        game_2p.players[0].add_card(victim_card)
    card.effect.trigger(game_2p, card, game_2p.players[1], game_2p.players[1])
    # Opponent has 3 stores, so 3 coins move
    assert game_2p.players[0].coins == 2
    assert game_2p.players[1].coins == 8
    event = game_2p.events.get_nowait()
    assert event.__class__.__name__ == "MoneyTaken"
    assert event.reason == card
    assert event.owed == 3


def test_take_coins_for_each_landmark(game_4p: MachiKoroGame):
    """
    Check that calculation of "coins for each landmark" is correct".
    """
    card = get_card_from_deck(DECK_LANDMARKS, "museum")  # TakeCoinsForEachLandmark
    lm = get_card_from_deck(DECK_LANDMARKS, "city_hall")
    game_4p.current_player = 1
    game_4p.players[0].landmarks.append(lm)
    game_4p.players[0].landmarks.append(lm)
    game_4p.players[0].coins = 10
    game_4p.players[1].landmarks.append(lm)
    game_4p.players[2].landmarks.append(lm)
    card.effect.trigger(game_4p, card, game_4p.players[1], game_4p.players[1])
    assert game_4p.players[0].coins == 4
    assert game_4p.players[1].coins == 14
    assert game_4p.players[2].coins == 2
    assert game_4p.players[3].coins == 5
    event = game_4p.events.get_nowait()
    assert event.__class__.__name__ == "MoneyTaken"
    assert event.owed == 3
    event = game_4p.events.get_nowait()
    assert event.__class__.__name__ == "MoneyTaken"
    assert event.owed == 6


def test_take_five_if_two_landmarks(game_2p: MachiKoroGame):
    """
    Check that we correctly take 5 coins from 2 landmark owners.
    """
    card = get_card_from_deck(
        DECK_LANDMARKS, "private_club"
    )  # TakeFiveCoinsIfTwoLandmarks
    lm = get_card_from_deck(DECK_LANDMARKS, "city_hall")
    game_2p.current_player = 1
    game_2p.players[0].landmarks = [lm, lm]
    game_2p.players[0].coins = 10
    card.effect.trigger(game_2p, card, game_2p.players[1], game_2p.players[1])
    assert game_2p.players[0].coins == 5
    assert game_2p.players[1].coins == 10
    event = game_2p.events.get_nowait()
    assert event.__class__.__name__ == "MoneyTaken"
    card.effect.trigger(game_2p, card, game_2p.players[0], game_2p.players[0])
    assert game_2p.players[0].coins == 5
    assert game_2p.players[1].coins == 10
    assert event.owed == 5


def test_evenly_distribute_coins(game_4p: MachiKoroGame):
    """
    Check that even coin distribution works and rounds up from bank.
    """
    card = get_card_from_deck(DECK_LANDMARKS, "park")  # EvenlyDistributeCoins
    game_4p.players[0].coins = 1
    game_4p.players[1].coins = 7
    game_4p.players[2].coins = 0
    game_4p.players[3].coins = 2
    card.effect.trigger(game_4p, card, game_4p.players[0], game_4p.players[0])
    # total = 10, avg = ceil(10/4) = 3, so everyone gets 3
    assert all(p.coins == 3 for p in game_4p.players)
    event = game_4p.events.get_nowait()
    assert event.__class__.__name__ == "MoneyDivided"
    assert event.coins == 3
    assert event.from_bank == 2
    assert event.total_coins == 10


def test_extra_turn(game_2p: MachiKoroGame):
    """
    Check that extra turn effect sets extra turn flag on player.
    """
    card = get_card_from_deck(DECK_LANDMARKS, "radio_tower")  # ExtraTurn
    assert not game_2p.players[1].extra_turn
    card.effect.trigger(game_2p, card, game_2p.players[1], game_2p.players[1])
    assert game_2p.players[1].extra_turn
    event = game_2p.events.get_nowait()
    assert event.__class__.__name__ == "GetExtraTurn"
    assert not event.no_effect


def test_insta_win(game_2p: MachiKoroGame):
    """
    Check that building Launch Pad calls for game end.
    """
    card = get_card_from_deck(DECK_LANDMARKS, "launch_pad")  # InstaWin
    card.effect.trigger(game_2p, card, game_2p.players[1], game_2p.players[1])
    assert game_2p.players[1].have_launch_pad == True


def test_built_loan_office(game_2p: MachiKoroGame):
    """
    Check that building Loan Office sets appropriate flags on player.
    """
    card = get_card_from_deck(DECK_LANDMARKS, "loan_office")  # BuiltLoanOffice
    assert not game_2p.players[1].have_loan_office
    card.effect.trigger(game_2p, card, game_2p.players[1], game_2p.players[1])
    assert game_2p.players[1].have_loan_office
    event = game_2p.events.get_nowait()
    assert event.__class__.__name__ == "NewLandmarkEffectActivated"
    assert event.builder_only


def test_persistent_effect(game_2p: MachiKoroGame):
    """
    Check that orange landmark effects apply ongoing effect to game instance.
    """
    card = get_card_from_deck(DECK_LANDMARKS, "city_hall")  # PersistentEffect
    card.effect.trigger(game_2p, card, game_2p.players[1], game_2p.players[1])
    assert Effect.NO_EARN_COMPENSATION_ONE_DICE in game_2p.active_effects
    event = game_2p.events.get_nowait()
    assert event.__class__.__name__ == "NewLandmarkEffectActivated"


def test_airport_cannot_build(game_2p: MachiKoroGame):
    """
    Check that airport effect applies if cannot build.
    """
    card = get_card_from_deck(DECK_LANDMARKS, "airport")
    card.effect.trigger(game_2p, card, game_2p.players[1], game_2p.players[1])
    event = game_2p.events.get_nowait()
    assert event.__class__.__name__ == "NewLandmarkEffectActivated"
    assert Effect.SKIP_BUILD_FOR_5_COINS in game_2p.active_effects
    game_2p.players[0].coins = 0
    game_2p.start(None, randomize_players=False)
    for _ in range(3):
        game_2p.events.get_nowait()
    event = game_2p.events.get_nowait()
    assert event.__class__.__name__ == "SkipBuild"
    event = game_2p.events.get_nowait()
    assert event.__class__.__name__ == "MoneyEarned"
    assert game_2p.players[0].coins == 5
