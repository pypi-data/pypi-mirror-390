# Forking

`Forking` is a Python context manager that run the code in a different
process.

That means funny business:

```pycon
>>> import os
>>> from forking import Forking
>>>
>>>
>>> with Forking():
...     os._exit(0)
>>> print("I will survive!")
I will survive!
>>>
```

Obviously side effects are only executed in the child process so not
visible to the parent:

```pycon
>>> i = 1
>>> with Forking():
...     i += 1
>>> print(i)
1
>>>
```

You can capture `stdout` and `stderr` though:

```python
child = Forking()
with child:
    print("Youpi")
print(child.stdout)
```

Note that we can't do `with Forking() as child` because the `as child`
part is not executed (as considered inside the with body).


You can also get info about the exit status of your process though
`child.exit` which contains `code`, `signal` and `has_core_dump`:

```pycon
>>> child = Forking()
>>> with child:
...     os._exit(12)
>>> print(child.exit.code)
12
>>>
```


Last trick, a `Forking` context can be reused (but its process will not):

```pycon
>>> child = Forking()
>>> with child:
...     os._exit(21)
>>> print(child.exit.code)
21
>>> with child:
...     os._exit(22)
>>> print(child.exit.code)
22
>>>
```
