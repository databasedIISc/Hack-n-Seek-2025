I hope you emember the `brainrot13` function. Well I have created another `super` function on it.

This requires you basic insights on binary numbers, ASCII Characters and XOR.
All you need to know is -

1. ASCII characters require 1 byte or 8 bit for representing them.
2. [XOR](https://medium.com/@Harshit_Raj_14/useful-properties-of-xor-in-coding-bitwise-manipulation-and-bitmasking-2c332256bd61) is an operation on 2 bits which is mentioned below -

```
0 XOR 0 = 0
0 XOR 1 = 1
1 XOR 0 = 1
1 XOR 1 = 0
```

My `super` function does the following -

1. For a brainrot13 string, I enclose it within `dbdth{...}`. Say `W` = `dbdth{my_example_string}`
2. I convert the whole ASCII string formed into binary, whose length is obviously a multiple of 8. Let the binary be denoted as `binW`
3. Now I take some key `K`(which you do not know), and make a new key `bigK` which is repetition of `K` such that the length of `bigK` = length of `W`.
   For example, if my key was `lock`, I have

---

dbdth{my_example_string}
locklocklocklocklocklock

---

4. Next we XOR each digit of the binary of `bigK` with `binW` to get the final encrypted binary!
   Example: Say binary of `bigK` = `01010100` and `binW` = `01101010`
   Then XOR will be = `00111110`, which is your superbrainrot13 of your word!

Your task is to reverse engineer the super function to get a string of format `dbdth{...}`, extract the word inside the braces and unbrainrot13 the same, just like you did before. Enclose your answer within `dbdth{...}` and submit!
One hint: since you are dealing with binaries: Make sure all binaries you deal with have same length, i.e. you might miss out initial zeros because usually people ignore it.

I have attached you a binary file with my `superbrainrot13` string! And just a hint, just look at the binary string carefully and re-read the problem to guess the key. No Frenzy Flags in this problem.

---

Thanks to @Par-R-S for helping me create this problem
