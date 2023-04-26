# %% [markdown]
# # Secure sorting networks explained
# 
# In this notebook, we develop some MPC protocols for securely sorting lists of secret-shared numbers. Concretely, we will show how to define functions sorting lists of secure MPyC integers into ascending order. The values represented by the secure integers and their relative order should remain completely secret.
# 
# The explanation below assumes some basic familiarity with the MPyC framework for secure computation. Our main goal is to show how existing Python code for (oblivious) sorting can be used to implement a secure MPC sorting protocol using the `mpyc` package. The modifications to the existing code are very limited.
# 
# ## Sorting networks
# 
# [Sorting networks](https://en.wikipedia.org/wiki/Sorting_network) are a classical type of comparison-based sorting algorithms. The basic operation (or, gate) in a sorting network is the *compare&swap* operation, which puts any two list elements $x[i]$ and $x[j]$, $i<j$, in ascending order. That is, only if $x[i]>x[j]$, elements $x[i]$ and $x[j]$ are swapped, and otherwise the compare&swap operation leaves the list unchanged. 
# 
# A sorting network specifies the exact sequence of compare&swap operations to be applied to a list of a given length $n$. The particular sequence depends only on $n$, the length of the input list. Even when the input list is already in ascending order, the sorting network will perform exactly as many---and actually the same---compare&swap operations as when the input list would be in descending order. 
# 
# For example, to sort a list of three numbers, one needs to perform three compare&swap operations with indices $(i,j)$ equal to $(0,1)$, then $(1,2)$, and finally once more $(0,1)$.
# 
# Below, we will use odd-even merge sort and bitonic sort, which are two well-known practical sorting networks. 
# 
# ## MPyC setup
# 
# A simple MPyC setup using 32-bit (default) secure MPyC integers suffices for the purpose of this demonstration.
# 
# At this point we also import the Python `traceback` module for later use.

# %%
from mpyc.runtime import mpc    # load MPyC
secint = mpc.SecInt()           # 32-bit secure MPyC integers
mpc.run(mpc.start())            # required only when run with multiple parties
import traceback                # to show some suppressed error messages
import math
import random

print(f"Paries: {len(mpc.parties)}")

# %% [markdown]
# ## Odd-even merge sort
# 
# Odd-even merge sort is an elegant, but somewhat intricate, sorting network. The details are nicely explained in the Wikipedia article [Batcher's Odd-Even Mergesort](https://en.wikipedia.org/wiki/Batcher_odd–even_mergesort). 
# 
# For our purposes, however, there is no need to understand exactly how this particular sorting network works. The only thing that we need to do is to grab the following  [example Python code](https://en.wikipedia.org/w/index.php?title=Batcher_odd%E2%80%93even_mergesort&oldid=969926478#Example_code) from this Wikipedia article.

# %%
def binary_search_insecure(x, a):
    low = 0
    high = len(x)-1
    if x[0] == a:
            return 0
    elif x[len(x)-1] == a:
        return len(x)-1
    else:
        while(low <= high):
            mid = int((low+high)/2)
            if x[mid]==a:
                return mid
            elif x[mid] > a:
                high = mid -1
            elif x[mid] < a:
                low = mid +1
        return -1  #returns -1 if the target does not exist
    
def binary_search(x, a):
    low = 0
    high = len(x)-1
   
    searching = True
    array_length = len(x)
    searches = int(math.log(array_length, 2))
    searches += 1

    mid = -1

    for i in range(searches):
        mid = (low+high)//2
        high = mpc.if_else(x[mid] > a, mid - 1, high)
        low = mpc.if_else(x[mid] < a, mid + 1, low)

        # display(low)
        # display(mid)
        # display(high)
        # display("")

    mid = mpc.if_else(x[mid] != a, -1, mid)

    return mid  #returns -1 if the target does not exist

# %%
n = 100
s = [(-1)**i * (i + n//2)**2 for i in range(n)]
s.sort()
s

# %% [markdown]
# We run the code on a simple example. Note that this code assumes that the length of the input list is an integral power of two.

# %%
random_index = random.randint(0, n-1)
a = s[random_index]
index = binary_search_insecure(s, a)
print(f"random_index = {random_index} ~ index = {index}")

# %%
random_index = random.randint(0, n-1)
a = s[random_index]
index = binary_search(s, a)
print(f"random_index = {random_index} ~ index = {index}")

# %% [markdown]
# We try to run this code on a list of secure MPyC integers.

# %%
random_index = random.randint(0, n-1)
a = s[random_index]
try:
    index = binary_search_insecure(s, a)
    print(f"random_index = {random_index} ~ index = {index}")
except:
    traceback.print_exc()

# %%
random_index = random.randint(0, n-1)
a = s[random_index]
x = list(map(secint, s))
x = mpc.seclist(x)
try:
    index = binary_search(x, a)
    print(f"random_index = {random_index} ~ index = {mpc.output(index)}")
except:
    traceback.print_exc()

# %%
mpc.run(mpc.shutdown())   # required only when run with multiple parties

# %% [markdown]
# The Python script [sort.py](sort.py) demos MPyC's built-in sorting method, which uses Batcher's merge-exchange sort (nonrecursive version of odd-even merge sort).

# %% [markdown]
# 


