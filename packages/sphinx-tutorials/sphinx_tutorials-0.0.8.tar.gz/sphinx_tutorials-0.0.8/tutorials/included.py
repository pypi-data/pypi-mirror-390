# - Title using `-`

# * Title using `*`

# = Title using `=`

# %% Title using `%%`

print("A simple code block")

# with a comment

# END

# <> A code block

print("A code block")

# END

# <> A collapsible code block
# collapse

print("A code block")

# END


# <> A collapsible (open) code block
# collapse: open

print("A code block")


# TABS

# %% tab_1

[i for i in range(5)]

# a comment

"""
Some text
"""

# %% tab 2

"""
This is how to include text.
"""

# END

print("Be careful. If this is followed by <> it does not get included")
# todo: maybe it needs to get fixed

# END

# TABS

# %% example

"ABS"

# END


# <> Imports


# %% New Title

print("If you include a separator, like some text")

"""
"""

# <> Imports


# %% using

# example code


"""
Now a plot
"""

# %% using matplotlib

print("ciao!")

# * check

print("ciao!")
