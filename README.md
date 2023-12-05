[![made-with-python](https://img.shields.io/badge/Made%20with-Python-1f425f.svg)](https://www.python.org/) [![MIT license](https://img.shields.io/badge/License-MIT-blue.svg)](https://lbesson.mit-license.org/) ![Maintainer](https://img.shields.io/badge/maintainer-Yuri_S_Villas_Boas-blue)

# Great Wall

Protocol and application for providing Kerckhoffian, 0-trust, deviceless coercion-resistance in self-custody. To understand the protocol, refer to the [executive summary.](./executive_summary.md)
References: [GreatWallT3](https://linktr.ee/greatwallt3)

## Reproducing Demo 1 Experiment:

The follow steps will allow easy memorization of the path demonstrated in the [demo 1 video](https://drive.proton.me/urls/GQZDRPBKE8#33ZVNJBXKAMd) within as little as 1-2 hours:

1. Download, install, and learn how to use [Anki](https://apps.ankiweb.net/) in your system.
2. Download and import [demo 1 Anki deck](https://github.com/Yuri-SVB/Great_Wall/blob/main/demos/GW_procedural_memory_1.apkg) in your Anki instance.
3. Study the deck.
4. Download (or clone from repository) [directory src](https://github.com/Yuri-SVB/Great_Wall/tree/main/src), and make sure your `main.py` file looks similar to [this version](https://github.com/Yuri-SVB/Great_Wall/blob/e8b1551c08a3d59ee8cf30f2b5dfa803556a00a6/src/main.py) of the `main.py` file (because this commit was used for demo 1).
5. In your system's terminal, open the directory, activate [python venv](https://docs.python.org/3/library/venv.html), install the dependencies and then run `main.py` file.
6. Enter ```viboniboasmofiasbrchsprorirerugugucavehistmiinciwibowifltuor``` as the required hidden password (also known as```SA0```).
7. You have, now, started to navigate the same tree as demonstrated in demo 1 from its root. Continue as practiced with the aforementioned Anki deck until the leave.
8. By confirming with input 1 to the correct leave, you should get the following output:

```console
53ffb290aa668cd5050e94aeecbb7046ce349d8ff775e409fcba45f6164a22d00e8cfb91e6836da62e7f7362cca30539b7f57f55e5c4a1cdf27a86997b99b2c6ee7760838ac0454e3e2f87714d303550b49063ff89934ecdb48e6c328f1c4561a9b7374232cdd8a71077653ca8091fc2b43b89f615ddac37aedfacd28bb605ba
```

**NOTE:** This is an **improper** [BIP39](https://github.com/bitcoin/bips/tree/master/bip-0039) seed, i.e., a seed that should **not** be used because it's trivially obtainable --- or ways to obtain it are published.
9. Just like the seed, all the addresses derived from it are **improper** and, therefore should not be used. One of them, obtained upon loading wallet with the seed in previous item, will be ```bc1q3qjatkwlrxvkah0uphr2vj3lqqd73l22n7djl9```.

10. In your favorite blockchain explorer, you can confirm that its first two transactions were, respectively, receiving 198964 Sats, and then having them removed back (before publication). One such example is [here](https://blockstream.info/address/bc1q3qjatkwlrxvkah0uphr2vj3lqqd73l22n7djl9).
Obs.: In cases like this, it's advisable to utilize a coinjoin service to preserve privacy.

## Using Great Wall in Beta:

Coming soon. An advanced, knowledgeable, tech-savvy reader, will, at this point, have understood what is to come and can improvise the steps by themself. In a nutshell, all you have to do is to securely manage* a brute-force resistant ```SA0```, true-randomly generate a path vector of ```L_i```'s, and memorize them procedurally as explained in the session above. For better effect, user can implement non-trivial **T**ime-**L**ock **P**uzzle, to impose desired time on derivation of ```SA3``` from ```SA0```. To prevent leakage of critical content through Anki, a simple scheme with salt and pepper can be done so to avoid the need to modify Anki, but we'll leave this for a next time.

* That is, either memorize it, or deterministically derive it from other brute-force resistant secret information, or symmetrically encrypt it with a master key falling back in one of 2 previous cases and manage well the encrypted database.
