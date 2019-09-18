from toolz import keyfilter, compose


def pick(whitelist, d):
    return keyfilter(lambda k: k in whitelist, d)


mapr = compose(list, map)
