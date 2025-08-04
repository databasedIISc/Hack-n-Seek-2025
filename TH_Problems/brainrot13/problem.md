One of the earliest Ciphers was [Caeser Cipher](https://en.wikipedia.org/wiki/Caesar_cipher) wherein the alphabets were rotated left/right by some value.
Among the 26 possible Caeser shift values, 13th was a fun one, since it was right in the middle. Famously, the Caeser Cipher with 13 rotation was coined **rot13**.

Now in 21st Century where word of the year of 2024 was `brainrot`, we come up with another extended version of this cipher, which is `brainrot13`. This is a composition of `brain` function on `rot13` of a string.

Here is a description of the brain function on the word "happy":

- Take the length of the word
- Add it to `h` -> `m`.
- Now subtract `m` from `a` to get `n`. (Everything is mod 26)
- Now Add `n` to `p` to get `d` and so on you change the sign things alternatively to finally get `mndlk`

Finally you get `brainrot13(happy)` -> `znqlx`.

You are given the encrypted flag after applying `brainrot13` on the your true answer, which is: `hwoqlhzanafhdwj`
Can you recover the original flag?

> [!NOTE]
> Enclose your answer within `dbdth{...}`

---

Thanks to @Par-R-S for helping me create this problem
