The basic idea behind the question(which is also deliberately set) is that when you decode the binary, it should contain `dbdth{` in the beginning. So you can guess the key by using the following property of XOR:

```
if A XOR B = C
then c XOR B = A
```

So you take `dbdthdbdthdbdthdbdth` (5 x 4) (why this? because the binary is 8 x 5 x 4 long) as key and perform XOR. You get `super` in the beginning. And this matches with the problem name, so you get the motivation that the key is `supersupersupersuper`.

Now after you XOR the binaries. You should get `dbdth{sorzetycjozbg}`! Yay!
Now just do unbrainrot13 the inner bracket value and get: `super_rot_xor`

So the flag is: `dbdth{super_rot_xor}`
