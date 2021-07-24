/* I know, I'm mad */
export function sane_if(pairs: [boolean, any][])  // yields undefined if we all fail
{                                                // of course, I was too lazy to implement a flag for that
                                                // so too bad if one of the cases actually returns undefined
                                               // and plus, js has no proper facilities to elegantly handle
                                              // multiple return values (unlike common lisp) :(
                                             // no, destructuring bind does not count
    let i = 0;
    let f = false;
    pairs.reduce(function (a, c) {
        i = !f ? (c[0] ? a : i) : i;
        return a + 1;
    }, 0);
    return pairs.concat(undefined)[i][1];
}

export function sane_switch<val_t, ret_t>(val: val_t, pairs: [val_t, ret_t][])
{
    return sane_if(pairs.map((c: [val_t, ret_t]) => [val === c[0], c[1]]));
}
/* Manic episode over */
