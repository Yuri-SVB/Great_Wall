# Great_Wall
Protocol and application for providing Kerckhoffian, 0-trust, deviceless coercion-resistance in self-custody.

## Reproducing Demo 1 Experiment:

The follow steps will allow easy memorization of the path demonstrated in demo 1 within as little as 1-2 hours:

1. Download, install, and learn how to use [Anki](https://apps.ankiweb.net/) in your system;
2. Download (or clone from repository) and import [demo 1 Anki deck](https://github.com/Yuri-SVB/Great_Wall/blob/main/demos/GW_procedural_memory_1.apkg);
3. Study deck;
4. Download (or clone from repository) [directory src](https://github.com/Yuri-SVB/Great_Wall/tree/main/src);
5. In your system's terminal, open the directory, activate venv and then run main.py;
6. Enter ```viboniboasmofiasbrchsprorirerugugucavehistmiinciwibowifltuor``` as the required input ```SA0```;
7. You have, now, started to navigate the same tree as demonstrated in demo 1 from it's root. Continue as practiced with the aforementioned Anki deck until the leave;
8. By confirming with input 1 to the correct leave, you should get the following output: ```53ffb290aa668cd5050e94aeecbb7046ce349d8ff775e409fcba45f6164a22d00e8cfb91e6836da62e7f7362cca30539b7f57f55e5c4a1cdf27a86997b99b2c6ee7760838ac0454e3e2f87714d303550b49063ff89934ecdb48e6c328f1c4561a9b7374232cdd8a71077653ca8091fc2b43b89f615ddac37aedfacd28bb605ba```. This is an **improper** BIP39 seed, _ie_ a seed that should **not** be used because it's trivially obtainable --- it or ways to obtain it are published;
9. Just like the seed, all the addresses derived from it are **improper** and, therefore should not be used. One of them, obtained upon loading wallet with the seed in previous item, will be ```bc1q3qjatkwlrxvkah0uphr2vj3lqqd73l22n7djl9```. In your favorite blockchain explorer, you can confirm that it's first two transactions were, respectively, receiving 198964 Sats, and then having them removed back (before publication). Obs.: in cases like that, it's advisable to utilize a coinjoin service to preserve privacy;

## Using Great Wall in Beta:

Coming soon. An advanced, knowledgeable, tech-savvy reader, will, at this point, have understood what is to come and can improvise the steps by themself. In a nutshell, all you have to do is to securely manage* a brute-force resistant ```SA0```, true-randomly generate a path vector of ```L_i```'s, and memorize them procedurally as explained in the session above. For better effect, user can implement non-trivial **T**ime-**L**ock **P**uzzle, to impose desired time on derivation of ```SA3``` from ```SA0```. To prevent leakage of critical content through Anki, a simple scheme with salt and pepper can be done so to avoid the need to modify Anki, but we'll leave this for a next time.

* That is, either memorize it, or deterministically derive it from other brute-force resistant secret information, or symmetrically encrypt it with a master key falling back in one of 2 previous cases and manage well the encrypted database.
