import os

names = {
    1: "tony-soprano", 2: "carmela-soprano", 3: "christopher-moltisanti",
    4: "paulie-gualtieri", 5: "silvio-dante", 6: "dr-jennifer-melfi",
    7: "junior-soprano", 8: "livia-soprano", 9: "adriana-la-cerva",
    10: "big-pussy-bonpensiero", 11: "meadow-soprano", 12: "a-j-soprano",
}

for number, name in names.items():
    if os.path.exists(f"{number}.png"):
        os.rename(f"{number}.png", f"{name}.png")