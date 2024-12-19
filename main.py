#! /usr/bin/env python3

from __future__ import annotations

from dataclasses import dataclass
from typing import TypeVar, Generic
from random import random
import matplotlib.pyplot as plt

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

    def merge(self, other):
        total = { v: self.counts.get(v, 0) + other.counts.get(v, 0) for v in set(self.counts) | set(other.counts) }
        return Sample(self.nb + other.nb, total)

    def freq_of(self, evt):
        return self.counts.get(evt, 0) / self.nb

def regular_sample(d, nb):
    s = Sample.empty()
    while s.nb < nb:
        s.add(d.sample())
    return s

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
d.add(W(0.01, 'a'))
d.add(W(0.01, 'b'))
d.add(W(0.02, 'c'))
d.add(W(0.02, 'd'))
d.add(W(0.04, 'e'))
d.add(W(0.90, 'z'))

def repeat_sample(sampler, repeat):
    s = Sample.empty()
    for _ in range(repeat):
        s = s.merge(sampler())
    return s

def data_freq_of(sampler, distrib, size, repeat, evt):
    return repeat_sample(lambda: sampler(distrib, size), repeat).freq_of(evt)

def range_data_freq_of(sampler, distrib, sizes, repeat, evt):
    return [data_freq_of(sampler, distrib, size, repeat, evt) for size in sizes]

def plot_perf_sampler(sampler, distrib, sizes, repeats, evt):
    data = range_data_freq_of(sampler, distrib, sizes, repeats, evt)
    plt.plot(data)

repeats = range(len(d.vals), 300)
plot_perf_sampler(regular_sample, d, repeats, 1000, 'a')
plot_perf_sampler(naive_full_sample, d, repeats, 1000, 'a')
plot_perf_sampler(better_full_sample, d, repeats, 1000, 'a')
plt.show()
