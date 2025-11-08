# mk2lib

**Machi Koro 2 Game Engine**  

A Python library for modeling and simulating the rules, components, and gameplay logic of *Machi Koro 2* boardgame that focuses on correctness, which could be used for AI training, trying out custom house rules or new cards, etc.

---

## Table of Contents

- [Features](#features)  
- [What is it not](#what-is-it-not)  
- [Getting Started](#getting-started)  
  - [Requirements](#requirements)  
  - [Installation](#installation)  
- [Usage](#usage)  
- [Tests](#tests)  
- [Contributing](#contributing)  
- [License](#license)
- [Acknowledgements](#acknowledgements)

---

## Features

- Complete implementation of core mechanics and rules of Machi Koro 2 (including landmark promo pack).  
- Full encapsulation of game logic within `mk2lib` and presentation abstraction, you can build any UI on top of it easily.  
- Rule enforcement: `mk2lib` tracks everything and checks move legality. You only need to input moves.  
- Event bus architecture that allows end application to observe game state and handle changes.  
- Support for 2-5 players.  
- Modular design: can be easily extended for new house rules, possible future addons, etc.  
- Support for fast game serialization/deserialization and AI agent friendly design.  
- Comprehensive pytest testsuite with 100% coverage to ensure implementation correctness.  

---

## What is it not

- A standalone ready-to-play game (unless you're willing to play from interactive Python REPL).  
- Machi Koro 2 AI/Bot (although it includes random fuzzing agent in test_fuzzing.py, which could be used as baseline for measuring AI performance).  

---

## Getting Started

### Requirements

- Python 3.10+  
- (Optional) `pytest` for running the test suite.

### Installation

Install module from PyPI:

```bash
pip install mk2lib
```

Or just clone this repository:

```bash
git clone https://github.com/ostrosablin/mk2lib.git
cd mk2lib
```

---

## Usage

Here's a minimal example to give you an idea how to use this library.

```python
from mk2lib import MachiKoroGame

# Initialize game with player ID 1 as owner.
game = MachiKoroGame(1)

# Player with ID 2 joins lobby.
game.join(2)

# Owner (1) starts game with landmark promo pack and random player order.
game.start(1, use_promo=True, randomize_players=True)

# Try to build a Convenience Store as current player.
game.build_card(None, "convenience_store")

# Read out all game's events.
while not game.events.empty():
    print(game.events.get())
```

You can find more complex example of game being (auto-)played from start to end in [test_fuzzing.py](https://github.com/ostrosablin/mk2lib/blob/master/tests/test_fuzzing.py).

---

## Tests

Tests are included in `tests/` directory within this repo. To run them, execute:

```
pytest --cov=mk2lib --cov-report=html
```

In root of repo. Ensure all tests pass before making changes or opening pull requests.

---

## Contributing

Contributions are welcome! If you'd like to help, please:

1. Fork the repository.
2. Create a branch with bugfix or feature.
3. Make changes and cover them with tests.
4. Open a pull request.

Please follow the existing code style, add documentation for new features and ensure tests cover your changes.

---

## License

`mk2lib` is licensed under GNU General Public License, Version 3.0. See [LICENSE](https://github.com/ostrosablin/mk2lib/blob/master/LICENSE) for full license text.

---

## Acknowledgements

**DISCLAIMER**: This is an unofficial fan project, based on board game ‘Machi Koro 2’. ‘Machi Koro’ is a trademark of its respective owners. This project is not affiliated with or endorsed by them in any way.
