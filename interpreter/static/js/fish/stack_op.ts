"use strict";
"use esversion: 6";

import { Stack, о, } from "./stack";

/* Sadly, nothing here is at all pure because JS is a big
 * mutable mess :(
 */

export function stack_dup(stack: Stack)
{
    о((s: Stack) => s.stack.push(s.stack[s.stack.length - 1]), stack);
}

export function stack_pop(stack: Stack)
{
    о((s: Stack) => s.stack.pop(), stack);
}

export function stack_swap(stack: Stack)
{
    о(function (s: Stack) {
        let tmp = s.stack[s.stack.length - 2];
        s.stack[s.stack.length - 2] = s.stack[s.stack.length - 1];
        s.stack[s.stack.length - 1] = tmp;
    }, stack);
}

export function stack_swap_three(stack: Stack)
{
    о(function (s: Stack) {
        const tmp = s.stack[s.stack.length - 1];
        s.stack[s.stack.length - 1] = s.stack[s.stack.length - 2];
        s.stack[s.stack.length - 2] = s.stack[s.stack.length - 3];
        s.stack[s.stack.length - 3] = tmp;
    }, stack);
}

export function stack_shift_right(stack: Stack)
{
    о((s: Stack) => s.stack.unshift(s.stack.pop()), stack);
}

export function stack_shift_left(stack: Stack)
{
    о((s: Stack) => s.stack.push(s.stack.shift()), stack);
}

export function stack_reverse(stack: Stack)
{
    о((s: Stack) => s.stack.reverse(), stack);
}

export function stack_pushlen(stack: Stack)
{
    о((s: Stack) => s.stack.push(s.stack.length), stack);
}

export function stack_givebirth(stack: Stack)
{
    о(function (s: Stack) {
        const n = s.stack.pop();
        s.o = {stack: s.stack.slice(s.stack.length - n), reg: null, o: null};
        s.stack = s.stack.slice(0, s.stack.length - n);
    }, stack);
}

export function stack_murderchild(stack: Stack)
{
    о(function (s: Stack) {
        s.stack = s.stack.concat(s.o.stack);
        s.o = null;  // bam
    }, stack, o =>o.o.o === null);
}

export function stack_reg(stack: Stack)
{
    о((s: Stack) => {
        if (s.reg === null) {
            s.reg = s.stack.pop();
        } else {
            s.stack.push(s.reg);
            s.reg = null;
        }
    }, stack);
}
