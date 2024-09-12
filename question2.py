EPSILON = '$'


def follow_of_upper_case(follow_set, first_sets_dict, next_letter, index, word):
    temp_set = first_set_from_dict(next_letter, first_sets_dict)
    print("ha")
    print(temp_set)

    if EPSILON not in temp_set:
        for terminal_letter in temp_set:
            follow_set.add(terminal_letter)
    elif EPSILON in temp_set:
        for terminal_letter in temp_set:
            if terminal_letter != EPSILON:
                follow_set.add(terminal_letter)

            if index + 2 <= len(word):
                next_next_letter = word[index + 2]
                print(next_next_letter)
                if next_next_letter.islower():
                    print(next_next_letter)
                    follow_set.add(next_next_letter)
                elif next_next_letter.isupper():
                    follow_set.update(
                        follow_of_upper_case(follow_set, first_sets_dict, next_next_letter, index + 1,
                                             word))

    return follow_set


def first_set_from_dict(symbol, first_sets_dict):
    first_set_set = set()
    for first_set in first_sets_dict[symbol]:
        first_set_set.add(first_set)

    return first_set_set


def follow_of(symbol, cf_grammar, first_sets_dict, first_key, terminals):
    follow_set = set()

    if symbol == first_key:
        follow_set.add(EPSILON)

    for head, production in cf_grammar.items():
        for rule in production:
            for word in rule:
                for index, letter in enumerate(word):
                    # Check if there's a next letter
                    if letter == symbol and index + 1 != len(word):
                        next_letter = word[index + 1]
                        print("check it")
                        if next_letter.isupper():
                            follow_set.update(
                                follow_of_upper_case(follow_set, first_sets_dict, next_letter, index, word))
                        elif next_letter.islower():
                            follow_set.add(next_letter)

                        print(f"Current letter: {letter}, Next letter: {next_letter}")

                    elif letter == symbol and index + 1 == len(word):
                        follow_set.update(follow_of(head, cf_grammar, first_sets_dict, first_key, terminals))
                        print(f"Current letter: {letter}, Next letter: None")

    return follow_set


def first_of(symbol, cf_grammar):
    first_set = set()

    for production in cf_grammar[symbol]:
        if production[0] == EPSILON:
            first_set.add(production[0])
        elif production[0] == symbol:
            return
        elif production[0][0].islower():
            first_set.add(production[0][0])
        elif production[0][0].isupper():
            first_set.update(first_of(production[0][0], cf_grammar))

    return first_set


def main():

    cf_grammar = {}
    non_terminals = set()
    terminals = set()

    print("Enter the cf_grammar (end with a blank line):")
    while True:
        rule = input().strip()
        if not rule:
            break
        head, production = rule.split("::=")
        head = head.strip()
        productions = [prod.split() for prod in production.split('|')]

        if head not in cf_grammar:
            cf_grammar[head] = []

        non_terminals.add(head)

        for prod in productions:
            for symbol in prod:

                # add Uppercase letters to non_terminals if they hadn't been added to set
                present = False

                if symbol.isupper() and len(symbol) == 1:
                    for i in non_terminals:
                        if i == symbol:
                            present = True

                    if not present:
                        non_terminals.add(symbol)

                # add small letters to terminals
                elif symbol.islower() and symbol != EPSILON and len(symbol) == 1:

                    present = False

                    for i in terminals:
                        if i == symbol:
                            present = True

                    if not present:
                        terminals.add(symbol)

        cf_grammar[head].append(prod)

    # was printing to test to see the sets and the dictionary
    print(cf_grammar)
    print(terminals)
    print(non_terminals)

    # first and follow sets dictionary

    first_sets_dict = {}
    follow_sets_dict = {}

    # function to get first sets
    for letter in non_terminals:

        if letter not in first_sets_dict:
            first_sets_dict[letter] = None

        first_sets_dict[letter] = first_of(letter, cf_grammar)
        print(first_sets_dict)

    # function to get follow sets
    for letter in non_terminals:

        if letter not in follow_sets_dict:
            follow_sets_dict[letter] = None

        for key in cf_grammar:
            first_key = key
            break

        follow_sets_dict[letter] = follow_of(letter, cf_grammar, first_sets_dict, first_key, terminals)
        print(follow_sets_dict)


if __name__ == "__main__":
    main()
