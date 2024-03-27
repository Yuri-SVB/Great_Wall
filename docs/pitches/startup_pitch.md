# Great Wall startup pitch

Great Wall is an elaborate key derivation scheme that yields a unique combination of information security properties through the exploitation of existing cryptographic techniques together with our proposed concept of **T**KBA or **T**acit [Knowledge-Based Authentication](https://en.wikipedia.org/wiki/Knowledge-based_authentication). The following are our achieved properties:

1. **Self-Custody** --- It's the basic premise of Bitcoin: The owner, and the owner alone is able to perform the protocol of access to their funds;
2. **Non-Obscurity** --- Another way to enunciate the [**Kerckhoff's Principle**](https://en.wikipedia.org/wiki/Kerckhoffs's_principle), or *The adversary perfectly understands the protocol, and it works nevertheless.* Reasons why it is **critically important** are discussed in the [executive summary / white paper](../white_paper_executive_summary/white_paper_executive_summary.md);
3. **Devicelessness** --- Loss, destruction, geographic separation, theft or threat to any (external) device doesn't interfere with the protocol;
4. **Monetization** --- Hence why a startup pitch;
5. **Coercion-Resistance** --- The main value propostition: how to utilize cryptographic techniques to resist to *physical violence*;
6. **No Unintended Negative Incentives** --- There is no material incentive to assassinate victim as a way to commit the stealing itself. It stems directly from item 2 and, once again, details at the [executive summary / white paper](../white_paper_executive_summary/white_paper_executive_summary.md);
7. **Interoperabiltiy** --- The protocol can be used on top of other protocols like **multi-signature schemes** and **inheritance protocols**;

Our method can be summarized as consisting of two basic components: the decades-old concept of 
[Time-Lock Puzzles](https://dspace.mit.edu/handle/1721.1/149822) (widely adopted in various applications like 
[memory-hard hashes / key-deriving functions](https://en.wikipedia.org/wiki/Argon2)), and our proposed concept of **T**KBA, or 
**Tacit** **K**owledge-**B**ased **A**authentication.

The former, TLP, makes sure the scheme takes an arbitrarily long time Delta T of a few hours, days, or even weeks, where such delay is previously setup by the user. Well established cryptographic techniques --- more about that on the [executive summary / white paper](../white_paper_executive_summary/white_paper_executive_summary.md) --- are used to make sure even an adversary with expensive machinery cannot crack this lengthy Delta T into a few minutes.

The latter, TKBA, makes sure the legit user's participation is **strictly necessary** for the completion of the derivation scheme. as a consequence,

> *The only way a coersive adversary aka thief can steal user's Bitcoin is to keep them under coercion for the entire time.*

If such Delta T has been setup to be long enough, such coercive operation becomes unfeasible and, hence, user has defended themself against physical robbery.

Monetization is possible through the *secure* outsourcing of TLP by user to the provider of such service. In other words, user pays for the convenience of freeing up their devices from the burden of having an intensive, memory hard, hours-, days- or weeks-long computation by *anonymously* paying a web-service to perform it to them.

For further information, check out [our demo](https://mega.nz/file/vfwhRTwZ#sP3hSRthQNssWRdcmD8XRNIeJX7Eq174ImY4eva_Pwo), [our official site](https://linktr.ee/greatwallt3) and our [executive summary / white paper](../white_paper_executive_summary/white_paper_executive_summary.md).
