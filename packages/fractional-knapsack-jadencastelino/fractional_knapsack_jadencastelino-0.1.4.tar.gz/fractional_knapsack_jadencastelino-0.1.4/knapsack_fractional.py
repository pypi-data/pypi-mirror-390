# knapsack_fractional.py

def frac_knapsack(values, weights, W):
    """
    values: list[int]
    weights: list[int]
    W: int (max weight)

    returns: float (max achievable value)
    """

    artifacts = []
    for v, w in zip(values, weights):
        artifacts.append((v, w, v/w))  # (value, weight, ratio)

    # sort by ratio desc
    artifacts.sort(key=lambda x: x[2], reverse=True)

    total = 0.0
    rem = W

    for v, w, r in artifacts:
        if rem <= 0:
            break
        if w <= rem:
            total += v
            rem -= w
        else:
            total += r * rem
            break
    return total


def main():
    N = int(input("Enter number of artifacts (N): "))
    W = int(input("Enter maximum bag weight (W): "))

    values = []
    weights = []

    for i in range(N):
        v = int(input(f"value of artifact {i+1}: "))
        w = int(input(f"weight of artifact {i+1}: "))
        values.append(v)
        weights.append(w)

    res = frac_knapsack(values, weights, W)
    print(f"Maximum total value achievable: {res:.2f}")


if __name__ == "__main__":
    main()
