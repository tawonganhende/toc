from collections import defaultdict, deque

EPSILON = '$'


def compute_first(grammar, non_terminals, terminals):
    first = defaultdict(set)
    computed = set()

    def first_of(symbol):
        if symbol in terminals:
            return {symbol}
        elif symbol == EPSILON:
            return {EPSILON}
        if symbol in computed:
            return first[symbol]
        computed.add(symbol)
        for rule in grammar[symbol]:
            for prod_symbol in rule:
                first[symbol].update(first_of(prod_symbol) - {EPSILON})
                if EPSILON not in first[prod_symbol]:
                    break
            else:
                first[symbol].add(EPSILON)
        return first[symbol]

    for non_terminal in non_terminals:
        first_of(non_terminal)

    return first


def compute_follow(grammar, non_terminals, first):
    follow = defaultdict(set)
    start_symbol = list(non_terminals)[0]
    follow[start_symbol].add('$')

    while True:
        updated = False
        for head, productions in grammar.items():
            for production in productions:
                trailer = follow[head]
                for i in reversed(range(len(production))):
                    symbol = production[i]
                    if symbol in non_terminals:
                        if follow[symbol].update(trailer):
                            updated = True
                        if EPSILON in first[symbol]:
                            trailer = trailer.union(first[symbol] - {EPSILON})
                        else:
                            trailer = first[symbol]
                    else:
                        trailer = first[symbol]
        if not updated:
            break
    return follow


def is_ll1(grammar, first, follow):
    for head, productions in grammar.items():
        seen = set()
        for production in productions:
            first_of_prod = set()
            for symbol in production:
                first_of_prod.update(first[symbol] - {EPSILON})
                if EPSILON not in first[symbol]:
                    break
            else:
                first_of_prod.update(follow[head])

            if seen & first_of_prod:
                return False
            seen.update(first_of_prod)
    return True


def build_parse_table(grammar, first, follow):
    parse_table = defaultdict(dict)
    for head, productions in grammar.items():
        for production in productions:
            first_of_prod = set()
            for symbol in production:
                first_of_prod.update(first[symbol] - {EPSILON})
                if EPSILON not in first[symbol]:
                    break
            else:
                first_of_prod.update(follow[head])

            for terminal in first_of_prod:
                parse_table[head][terminal] = production
    return parse_table


def parse_string(parse_table, start_symbol, input_string):
    input_string += '$'
    stack = deque([start_symbol, '$'])
    pointer = 0
    state_counter = 0

    print(f"{'State':<10}{'String':<15}{'Stack':<15}{'Rule'}")
    while stack:
        state_counter += 1
        stack_top = stack.pop()
        current_symbol = input_string[pointer]

        if stack_top == current_symbol == '$':
            print(f"{state_counter:<10}{input_string[pointer:]:<15}{''.join(stack):<15}Accepted")
            return True

        elif stack_top == current_symbol:
            print(f"{state_counter:<10}{input_string[pointer:]:<15}{''.join(stack):<15}Matched '{stack_top}'")
            pointer += 1

        elif stack_top.isupper():
            if current_symbol in parse_table[stack_top]:
                rule = parse_table[stack_top][current_symbol]
                print(
                    f"{state_counter:<10}{input_string[pointer:]:<15}{''.join(stack):<15}{stack_top} ::= {' '.join(rule)}")
                stack.extend(reversed([s for s in rule if s != EPSILON]))
            else:
                print(
                    f"{state_counter:<10}{input_string[pointer:]:<15}{''.join(stack):<15}Error: No rule for {stack_top} with input {current_symbol}")
                return False
        else:
            print(
                f"{state_counter:<10}{input_string[pointer:]:<15}{''.join(stack):<15}Error: Unexpected symbol {stack_top}")
            return False

    return False


def main():
    grammar = defaultdict(list)
    non_terminals = set()
    terminals = set()

    print("Enter the grammar (end with a blank line):")
    while True:
        rule = input().strip()
        if not rule:
            break
        head, production = rule.split("::=")
        head = head.strip()
        productions = [prod.split() for prod in production.split('|')]

        non_terminals.add(head)
        for prod in productions:
            for symbol in prod:
                if symbol.isupper():
                    non_terminals.add(symbol)
                elif symbol != EPSILON:
                    terminals.add(symbol)
            grammar[head].extend(productions)

    first = compute_first(grammar, non_terminals, terminals)
    follow = compute_follow(grammar, non_terminals, first)

    print("\nFIRST sets:")
    for non_terminal in non_terminals:
        print(f"{non_terminal}: {first[non_terminal]}")

    print("\nFOLLOW sets:")
    for non_terminal in non_terminals:
        print(f"{non_terminal}: {follow[non_terminal]}")

    if is_ll1(grammar, first, follow):
        print("\nThe grammar is LL(1) parseable.")
        parse_table = build_parse_table(grammar, first, follow)

        print("\nParse Table:")
        for non_terminal, row in parse_table.items():
            for terminal, production in row.items():
                print(f"M[{non_terminal}, {terminal}] = {' '.join(production)}")

        input_string = input("\nEnter a string to parse: ")
        if not parse_string(parse_table, list(non_terminals)[0], input_string):
            print(f"\nThe string '{input_string}' is not accepted by the grammar.")
    else:
        print("\nThis grammar is not LL(1) parseable.")


if __name__ == "__main__":
    main()
