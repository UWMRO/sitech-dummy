from telescope import telescope

t = telescope()

# test altaz --> ra / dec
t.set_azalt(20, 30)
print(t)
t.set_coords(20, 30)
print(t)