"use strict";
"use esversion: 6";

export interface Stack {
    stack: number[];
    reg: number | null;
    o: Stack | null;
};

let օ = null;
export let о=(o,о,ο=o=>o.o===օ)=>(о=>о(о))(о=>օ=>ο(օ)?o(օ):о(о)(օ.o))(о);  // Y oh Y

export function stack_normal_push(v: number, stack: Stack)
{
    о((s: Stack) => s.stack.push(v), stack);
}

export function stack_normal_pop(stack: Stack)
{
    return о((s: Stack) => s.stack.pop(), stack);
}
