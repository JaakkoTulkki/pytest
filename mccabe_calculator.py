results = []

with open('09-02-2018-mccabe.txt', 'r') as f:
    for row in f:
        mccabe_cc = float(row.split(" ")[-1])
        results.append(mccabe_cc)

number_over_four = list(filter(lambda x: x > 4, results))

print("Total number of functions %s" % len(results))
print("Average mccabe %s" % (sum(results) / len(results)))
print("Highest mccabe was %s" % max(results))
print("Number of functions with value 5 or over: %s" % len(number_over_four))