This problem I admit is a bit hard, since it assumes some knowledge about C.

Idea is that C integers are usually 32 bit, so they tend to overflow i.e. 2^31 + 1 will loop around and become -2^31 (or INT_MIN).

Since you were not given the source code, you woudn't know. But then You were given 2 clues to think about this, 1) C shop (so C language) 2) Sale numbers are overflowing. So integer overflow.

Now if you try some huge number say, 102983094, you get integer overflow and your balance < 1200 initial balance. So once you buy from option 1, this balance gets add up to your BANK ACCOUNT (because subtracting a negative number adds up).
This should give you enough balance to buy the flag from Option 2.

Answer: `dbdth{c_integer_overflow_is_cliche}`

- Frenzy Flag: Try some other huge number to get negative balance. You should get `dbdth{c_shop_negative_balance}`
