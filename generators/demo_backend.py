#!/usr/bin/python3
"""
Demo backend that prints some
stats about the U-Boot build
"""
import json

def main():
    """ Main """
    log = json.load(open("log.json"))

    testcases = [
        ("U-Boot git repo setup ", "clean_repo_checkout"),
        ("U-Boot build total    ", "@build"),
        ("U-Boot build raw      ", "@compile"),
        ("U-Boot total          ", "build_uboot"),
        ]

    # Get testcase begin and end times
    times = map(lambda tc: (tc[0], [e['duration']
                                    for e in log
                                    if e['type'] == ['testcase', 'end'] and e['name'] == tc[1]][0]),
                testcases)

    # Print values
    for name, time in times:
        print(f"{name}: {time:.2f}s")

if __name__ == "__main__":
    main()
