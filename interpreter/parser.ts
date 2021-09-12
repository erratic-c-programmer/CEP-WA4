type Atom = number | string
type Expr = Atom | Expr[]

type prim_pt = string | prim_pt[]  // for initial parse (parse_i)

function parse_expr(expr: string)
{
    function parse_i()
    {
        // Stage I: primitive str -> list of strings
        let ret: prim_pt[] = [];
        let i: number = 0;
        let lwa: boolean = false;  // last was atom

        for (const c of expr) {
            if (c !== ' ') {
                if (lwa === true) {
                    ret[i] += c;
                } else {
                    ret.push(c);
                    i++;
                }
            } else {
                lwa = false;
            }
        }
    }
}
