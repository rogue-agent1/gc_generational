#!/usr/bin/env python3
"""Generational Garbage Collector — young/old generation with promotion."""
import sys

class GCObject:
    _id = 0
    def __init__(self, size=1):
        GCObject._id += 1; self.id = GCObject._id
        self.size, self.refs = size, []
        self.generation = 0; self.age = 0; self.marked = False
    def __repr__(self): return f"Obj({self.id}, gen={self.generation}, age={self.age})"

class GenerationalGC:
    def __init__(self, young_limit=10, promote_age=3):
        self.young, self.old = [], []
        self.roots = []; self.young_limit = young_limit
        self.promote_age = promote_age
        self.stats = {'minor': 0, 'major': 0, 'collected': 0, 'promoted': 0}
    def allocate(self, size=1):
        obj = GCObject(size); self.young.append(obj)
        if len(self.young) >= self.young_limit: self.minor_gc()
        return obj
    def add_root(self, obj): self.roots.append(obj)
    def _mark(self, obj):
        if obj.marked: return
        obj.marked = True
        for ref in obj.refs: self._mark(ref)
    def minor_gc(self):
        self.stats['minor'] += 1
        for obj in self.young + self.old: obj.marked = False
        for root in self.roots: self._mark(root)
        surviving = []; collected = 0
        for obj in self.young:
            if obj.marked:
                obj.age += 1
                if obj.age >= self.promote_age:
                    obj.generation = 1; self.old.append(obj); self.stats['promoted'] += 1
                else: surviving.append(obj)
            else: collected += 1
        self.young = surviving; self.stats['collected'] += collected
    def major_gc(self):
        self.stats['major'] += 1
        for obj in self.young + self.old: obj.marked = False
        for root in self.roots: self._mark(root)
        collected = 0
        self.old = [o for o in self.old if o.marked or not (collected := collected + 1)]
        self.young = [o for o in self.young if o.marked]
        self.stats['collected'] += collected
    def status(self):
        return f"Young: {len(self.young)}, Old: {len(self.old)}, Stats: {self.stats}"

if __name__ == "__main__":
    gc = GenerationalGC(young_limit=5, promote_age=2)
    root = gc.allocate(); gc.add_root(root)
    for i in range(15):
        obj = gc.allocate()
        if i % 3 == 0: root.refs.append(obj)
    gc.major_gc()
    print(gc.status())
