#! /usr/bin/env python3

from __future__ import annotations

from dataclasses import dataclass
from typing import TypeVar, Generic
from random import random

T = TypeVar("T")

@dataclass
class W(Generic[T]):
    weight: float
    val: T

@dataclass
class Distribution(Generic[T]):
    sum: float
    vals: list[W[W[T]]]

    @staticmethod
    def empty() -> Distribution[T]:
        return Distribution(0, [])

    def add(self, w):
        self.vals.append(W(self.sum, w))
        self.sum += w.weight

    def sample(self) -> T:
        pick = random() * self.sum
        idx = self.dichotomy(0, pick, len(self.vals))
        return self.vals[idx].val.val

    def dichotomy(self, lo, tgt, hi):
        if lo + 1 == hi:
            return lo
        mid = (lo + hi) // 2
        if self.vals[mid].weight <= tgt:
            return self.dichotomy(mid, tgt, hi)
        else:
            return self.dichotomy(lo, tgt, mid)

@dataclass
class Sample(Generic[T]):
    nb: int
    counts: dict[T, int]

    @staticmethod
    def empty():
        return Sample(0, {})

    def add(self, v):
        self.nb += 1
        self.counts[v] = self.counts.get(v, 0) + 1

    def delta(self, distr):
        e = {}
        for ww in distr.vals:
            value = ww.val.val
            real_weight = ww.val.weight / distr.sum
            est_weight = self.counts.get(value, 0) / self.nb
            e[value] = (real_weight, est_weight)
        return e


def naive_full_sample(d, nb):
    s = Sample.empty()
    for ww in d.vals:
        s.add(ww.val.val)
    while s.nb < nb:
        s.add(d.sample())
    return s

def better_full_sample(d, nb):
    s = Sample.empty()
    quota = { ww.val.val for ww in d.vals }
    for ww in d.vals:
        s.add(ww.val.val)
    while s.nb < nb:
        r = d.sample()
        if r in quota:
            quota.remove(r)
        else:
            s.add(r)
    return s

d = Distribution.empty()
d.add(W(0.1, 'a'))
d.add(W(0.1, 'b'))
d.add(W(9.8, 'c'))
s1 = naive_full_sample(d, 30)
s2 = better_full_sample(d, 30)
print(s1)
print(s2)

e1 = s1.delta(d)
e2 = s2.delta(d)
print(e1)
print(e2)








