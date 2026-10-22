"""Focused checks for the publication fixes; run with unittest from the repo root."""
import ast
import copy
import os
from pathlib import Path
import runpy
import sys
import tempfile
import unittest
from unittest.mock import patch

os.environ['SDL_VIDEODRIVER'] = 'dummy'
os.environ['SDL_AUDIODRIVER'] = 'dummy'
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = '1'
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
os.chdir(ROOT)

import pygame
pygame.init()
import main
import menu2
import board
from bank import Bank
from player import Player
from properties import buy_property
from ai_agent import AIAgent


class FixChecks(unittest.TestCase):
    def setUp(self):
        os.chdir(ROOT)
        pygame.init()
        pygame.display.set_mode((568, 571))
        pygame.event.clear()

    def home_definitions(self):
        tree = ast.parse((ROOT / 'home.py').read_bytes())
        tree.body = tree.body[:next(i for i, node in enumerate(tree.body) if isinstance(node, ast.While))]
        scope = {'__name__': 'review_only'}
        exec(compile(tree, 'home.py', 'exec'), scope)
        return scope

    def test_invalid_time_inputs_do_not_crash(self):
        popup = self.home_definitions()['abridged_popup']
        for text in ('', '0', '\u00b2'):
            with self.subTest(text=text):
                events = [pygame.event.Event(pygame.MOUSEBUTTONDOWN, pos=(250, 290), button=1)]
                events += [pygame.event.Event(pygame.KEYDOWN, key=0, unicode=char) for char in text]
                events += [pygame.event.Event(pygame.MOUSEBUTTONDOWN, pos=(450, 400), button=1)]
                batches = iter([events, [pygame.event.Event(pygame.MOUSEBUTTONDOWN, pos=(530, 65), button=1)]])
                with patch.object(pygame.event, 'get', side_effect=lambda: next(batches)):
                    self.assertIsNone(popup(pygame.display.get_surface()))

    def test_positive_time_by_click_or_enter(self):
        popup = self.home_definitions()['abridged_popup']
        for use_enter in (False, True):
            with self.subTest(use_enter=use_enter):
                events = [pygame.event.Event(pygame.MOUSEBUTTONDOWN, pos=(250, 290), button=1),
                          pygame.event.Event(pygame.KEYDOWN, key=pygame.K_5, unicode='5')]
                events += [pygame.event.Event(pygame.KEYDOWN, key=pygame.K_RETURN, unicode='')] if use_enter else [
                    pygame.event.Event(pygame.MOUSEBUTTONDOWN, pos=(450, 400), button=1)]
                with patch.object(pygame.event, 'get', return_value=events):
                    self.assertEqual(popup(pygame.display.get_surface()), 5)

    def run_setup(self, positions, result=None):
        index = 0
        def event_batch():
            nonlocal index
            point = positions[index]
            index += 1
            return [pygame.event.Event(pygame.QUIT)] if point is None else [
                pygame.event.Event(pygame.MOUSEBUTTONDOWN, pos=point, button=1)]
        with patch.object(pygame.mouse, 'get_pos', side_effect=lambda: positions[index] or (0, 0)), \
             patch.object(pygame.event, 'get', side_effect=event_batch), \
             patch.object(menu2, 'main_game_loop', return_value=result) as game, \
             patch.object(menu2.subprocess, 'run') as restart, \
             patch.object(menu2.time, 'sleep'):
            with self.assertRaises(SystemExit):
                menu2.load_menu()
            return game.call_args_list, restart.call_args_list

    def test_empty_and_partial_setup_are_rejected(self):
        for positions in ([(330, 365), None], [(120, 200), (70, 150), (330, 365), None],
                          [(120, 200), (70, 150), (330, 70), (330, 365), None]):
            with self.subTest(positions=positions):
                self.setUp()
                games, restarts = self.run_setup(positions)
                self.assertEqual(games, [])
                self.assertEqual(restarts, [])

    def test_complete_setup_and_restart_interpreter(self):
        games, restarts = self.run_setup([(60, 200), (70, 150), (330, 365)], result='menu')
        self.assertEqual(len(games), 1)
        players = games[0].args[0]
        self.assertEqual(len(players), 2)
        self.assertEqual(sum(p.is_ai for p in players), 1)
        command = restarts[0].args[0]
        self.assertEqual(command[0], sys.executable)
        self.assertEqual(command[1:3], ['-X', 'utf8'])
        self.assertEqual(Path(command[3]), ROOT / 'property_tycoon.py')

    def test_empty_game_returns_to_menu(self):
        self.assertEqual(main.main_game_loop([]), 'menu')

    def test_bankruptcy_releases_assets_without_attribute_error(self):
        player = Player(None, (255, 0, 0))
        player.properties = [{'name': 'The Old Creek'}]
        player.colour_group_owned = ['Brown']
        tiles = [{'name': 'The Old Creek', 'player': player.token_colour, 'mortgaged': True, 'houses': 2, 'hotels': 0}]
        messages = []
        self.assertIs(main.declare_bankruptcy(player, tiles, Bank(), messages), player)
        self.assertEqual(player.properties, [])
        self.assertEqual(player.colour_group_owned, [])
        self.assertEqual(tiles[0]['player'], 'Bank')
        self.assertFalse(tiles[0]['mortgaged'])
        self.assertEqual(tiles[0]['houses'], 0)
        self.assertIn('bankrupt', messages[-1])

    def test_actual_purchase_price_and_no_money_creation(self):
        for balance, price, allowed in ((60, None, True), (59, None, False), (40, 40, True),
                                         (70, 80, False), (100, 0, False), (100, -1, False)):
            with self.subTest(balance=balance, price=price):
                player = Player(None, (255, 0, 0))
                player.laps_completed = 1
                player.balance = balance
                tile = copy.deepcopy(board.load_board('board_data.json')['board'][1])
                bank = Bank()
                buy_property(player, tile, bank, [], price=price)
                self.assertEqual(bool(player.properties), allowed)
                self.assertEqual(player.balance + bank.balance, balance + 50000)
                if allowed:
                    self.assertEqual(tile['player'], player.token_colour)
                    self.assertEqual(player.balance, balance - (60 if price is None else price))
                else:
                    self.assertEqual(tile['player'], 'Bank')
                    self.assertEqual(player.balance, balance)

    def test_non_property_and_first_lap_restrictions_remain(self):
        player = Player(None, (255, 0, 0))
        tile = copy.deepcopy(board.load_board('board_data.json')['board'][1])
        buy_property(player, tile, Bank(), [])
        self.assertEqual(player.properties, [])
        player.laps_completed = 1
        buy_property(player, {'name': 'Go', 'can_be_bought': False}, Bank(), [])
        self.assertEqual(player.properties, [])

    def test_board_helper_uses_existing_asset(self):
        board.draw_board(pygame.display.get_surface())
        self.assertIn('\u00a3', board.load_board('board_data.json')['notes']['house_and_hotel_costs']['brown_blue']['hotel'])
        self.assertEqual(board.load_house_and_hotel_costs('board_data.json')['brown_blue']['house'], 50)

    def test_ai_can_sell_buildings_with_the_existing_bank(self):
        player = Player(None, (255, 0, 0))
        player.properties = [{'name': 'The Old Creek', 'group': 'Brown', 'houses': 1, 'hotels': 0}]
        tiles = board.load_board('board_data.json')['board']
        AIAgent(player).sell_houses_hotels(tiles, Bank(), [])
        self.assertEqual(player.properties[0]['houses'], 0)
        self.assertEqual(player.balance, 1550)

    def test_launcher_and_legacy_main_from_another_directory(self):
        for entry in ('property_tycoon', ROOT / 'property_tycoon.py', ROOT / 'main.py'):
            with self.subTest(entry=entry), tempfile.TemporaryDirectory() as temporary:
                pygame.init()
                pygame.event.clear()
                frames = []
                original_flip = pygame.display.flip
                def close_after_first_frame():
                    original_flip()
                    frames.append(pygame.display.get_surface().get_size())
                    pygame.event.post(pygame.event.Event(pygame.QUIT))
                os.chdir(temporary)
                with patch.object(pygame.display, 'flip', side_effect=close_after_first_frame):
                    if isinstance(entry, str):
                        runpy.run_module(entry, run_name='__main__')
                    else:
                        try:
                            runpy.run_path(str(entry), run_name='__main__')
                        except SystemExit:
                            pass
                self.assertEqual(frames[0], (568, 571))
                self.assertEqual(Path.cwd(), ROOT)


if __name__ == '__main__':
    unittest.main()
