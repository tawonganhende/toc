EPSILON = '$'


def is_ll1(first_sets_dict, follow_sets_dict, cf_grammar):
    for non_terminal, productions in cf_grammar.items():
        first_sets = []

        for production in productions:
            first_set = set()

            # Calculate first set for this production, similar to your first_of function
            for word in production:
                for symbol in word:
                    if symbol == EPSILON:
                        first_set.add(EPSILON)
                        break
                    elif symbol.islower():  # Terminal symbol
                        first_set.add(symbol)
                        break
                    elif symbol.isupper():  # Non-terminal symbol
                        first_set.update(first_sets_dict[symbol])
                        if EPSILON not in first_sets_dict[symbol]:  # Stop if no epsilon
                            break

            first_sets.append(first_set)

        # Check for intersections between first sets
        for i in range(len(first_sets)):
            for j in range(i + 1, len(first_sets)):
                if first_sets[i].intersection(first_sets[j]):
                    print("This grammar is not LL(1) parseable\n")
                    return False

        # Check for epsilon and follow set intersection
        for first_set in first_sets:
            if EPSILON in first_set:
                first_set.remove(EPSILON)
                if first_set.intersection(follow_sets_dict[non_terminal]):
                    print("This grammar is not LL(1) parseable\n")
                    return False

    print("This grammar is LL(1) parseable\n")
    return True


def follow_of_upper_case(follow_set, first_sets_dict, next_letter, index, word):
    temp_set = first_set_from_dict(next_letter, first_sets_dict)
    # print("ha")
    # print(temp_set)

    if EPSILON not in temp_set:
        for terminal_letter in temp_set:
            follow_set.add(terminal_letter)
    elif EPSILON in temp_set:
        for terminal_letter in temp_set:
            if terminal_letter != EPSILON:
                follow_set.add(terminal_letter)

            if index + 2 <= len(word):
                next_next_letter = word[index + 2]

                if next_next_letter.islower():

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
                        if next_letter.isupper():
                            follow_set.update(
                                follow_of_upper_case(follow_set, first_sets_dict, next_letter, index, word))
                        elif next_letter.islower():
                            follow_set.add(next_letter)

                        # used print statement to check if code was seeing the next letter
                        # print(f"Current letter: {letter}, Next letter: {next_letter}")

                    elif letter == symbol and index + 1 == len(word):
                        follow_set.update(follow_of(head, cf_grammar, first_sets_dict, first_key, terminals))
                        # print(f"Current letter: {letter}, Next letter: None")

    return follow_set


def build_parse_table(cf_grammar, first_sets_dict, follow_sets_dict):
    parse_table = {}
    for non_terminal, productions in cf_grammar.items():
        parse_table[non_terminal] = {}
        for production in productions:
            production_first_set = set()
            for word in production:
                for symbol in word:
                    if symbol.islower():
                        production_first_set.add(symbol)
                        break
                    elif symbol.isupper():
                        production_first_set.update(first_sets_dict[symbol])
                        if EPSILON not in first_sets_dict[symbol]:
                            break
                    if EPSILON in production_first_set:
                        production_first_set.remove(EPSILON)
                        production_first_set.update(follow_sets_dict[non_terminal])

            for terminal in production_first_set:
                parse_table[non_terminal][terminal] = production

    return parse_table


def parse_string(input_string, parse_table, start_symbol):
    stack = [start_symbol, '$']
    input_string += '$'
    index = 0

    print(f"{'State':<10}{'Input String':<20}{'Stack':<20}{'Rule':<20}")
    while stack:
        top = stack.pop()
        current_input = input_string[index]

        if top == current_input == '$':
            print(f"{'Accept':<10}{input_string[index:]:<20}{''.join(stack):<20}{'':<20}")
            return True

        if top.islower() or top == EPSILON:
            if top == current_input:
                index += 1
                print(f"{'Match':<10}{input_string[index:]:<20}{''.join(stack):<20}{'':<20}")
            else:
                print(f"{'Error':<10}{input_string[index:]:<20}{''.join(stack):<20}{'':<20}")
                return False
        elif top.isupper():
            if current_input in parse_table[top]:
                rule = parse_table[top][current_input]
                print(f"{'Apply':<10}{input_string[index:]:<20}{''.join(stack):<20}{top + ' -> ' + ' '.join(rule):<20}")
                if rule != [EPSILON]:
                    stack.extend(reversed(rule))
            else:
                print(f"{'Error':<10}{input_string[index:]:<20}{''.join(stack):<20}{'':<20}")
                return False
        else:
            print(f"{'Error':<10}{input_string[index:]:<20}{''.join(stack):<20}{'':<20}")
            return False

    return False


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
    print("CFG: " + str(cf_grammar))
    print("Terminals: " + str(terminals))
    print("Non Terminals: " + str(non_terminals))
    print(" ")

    # first and follow sets dictionary

    first_sets_dict = {}
    follow_sets_dict = {}

    # function to get first sets
    for letter in non_terminals:

        if letter not in first_sets_dict:
            first_sets_dict[letter] = None

        first_sets_dict[letter] = first_of(letter, cf_grammar)

    for head, production in first_sets_dict.items():
        print("The First Set for " + str(head) + " : " + str(production))

    # function to get follow sets
    for letter in non_terminals:

        if letter not in follow_sets_dict:
            follow_sets_dict[letter] = None

        for key in cf_grammar:
            first_key = key
            break

        follow_sets_dict[letter] = follow_of(letter, cf_grammar, first_sets_dict, first_key, terminals)
        #print(follow_sets_dict)

    for head, production in follow_sets_dict.items():
        print("The Follow Set for " + str(head) + " : " + str(production))

    if is_ll1(first_sets_dict, follow_sets_dict, cf_grammar):
        parse_table = build_parse_table(cf_grammar, first_sets_dict, follow_sets_dict)
        input_string = input("Enter a string to parse: ").strip()
        if all(c in terminals for c in input_string):
            if parse_string(input_string, parse_table, first_key):
                print("The string is accepted.")
            else:
                print("The string is rejected.")
        else:
            print("The string contains illegal symbols.")
    else:
        print("The grammar is not LL(1), parsing cannot proceed.")


if __name__ == "__main__":
    main()
