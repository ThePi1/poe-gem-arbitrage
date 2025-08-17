def main():
  while True:
    fossil_name = input("Fossil name: ")
    fossil_count = int(input("Number of fossils: "))
    desired_ratio = float(input("Desired ratio: "))

    ratios = [desired_ratio-1, desired_ratio, desired_ratio+1]

    for r in ratios:
      print(f"{fossil_name}: {fossil_count//r}div ({fossil_count/r:.2f}) : {(fossil_count//r)*r} fossils @ {r}:1")

main()