# randomlib (module: ramlib)

A simple random library with a Python prototype and a main C version that you can use in your projects for simple random tasks.

## Overview

`randomlib` (module: `ramlib`) is a simple, independent, and deterministic library for generating pseudo-random numbers based on time.  
It uses multiple layers of temporal granularity (milliseconds, microseconds, nanoseconds, and timestamp) combined with bitwise operations and dynamic multipliers.

Ideal for pseudo-randomness experiments, simulations, seed generation, and environments without complex external dependencies.

## Installation

```bash
pip install ramlib-samjamsh

```

## Usage
```
from ramlib import genrandom

# Get & Print a random value
start = 1
end = 10

random_value = genrandom(start, end)
print("\nRandom Value:", random_value.getnew())      # get a random value once
print()

for i in range(5):
    newrandom = random_value.generate(start, end)    # get a random value multiple times
    print("New Random:", newrandom)
print()
```