#!/usr/bin/env python3
import sys
import os.path
import subprocess

USAGE = ("Usage: tocc <sourcefile> <output_c>.c <output_binary>\n"
        "       tocc <sourcefile> <output_dot>.dot <output_image>.png\n")

class CompileError(Exception):
    pass

class SyntaxError(CompileError):
    pass

class SemanticError(CompileError):
    pass

class DFA():
    def __init__(self, Q, E, q0, d, F):
        check_consistency(E, Q, d, q0, F)
        self.Q = list(Q)
        if self.Q[0] != q0:
            i = self.Q.index(q0)
            self.Q[i] = self.Q[0]
            self.Q[0] = q0
        self.E = list(E)
        self.q0 = q0
        self.d = d
        self.F = list(F)

    def compile_to_dot(self):
        lines = [
            "digraph DFA{"
        ]
        states = list(map(
            lambda x: (
                f"\t{x} [shape=\"doublecircle\"]"
                if x in self.F else
                f"\t{x} [shape=\"circle\"]"
            ),
            self.Q
        ))
        states.append(
            '\t__ [label="", fixedsize="false", width=0, height=0, shape=none]'
        )
        lines.extend(states)
        lines.extend([
            f"\t{q1} -> {self.d[q1][symbol]} [label=\"{symbol}\"]"
            for q1 in self.d.keys()
            for symbol in self.d[q1]
        ])
        lines.append(
            f"\t__ -> {self.q0}"
        )
        lines.append("}")
        return "\n".join(lines)

    def compile_to_c(self):
        preprocessing = [
            "#include<stdio.h>",
            "#include<stdlib.h>"
        ]
        transition_function = [
            "int transition(int q, char b){"
        ]
        for i in range(len(self.Q)):
            transition_function.append(
                f"\tif(q == {i}){{"
            )
            for letter in self.E:
                transition_function.append(
                    f"\t\tif(b == '{letter}'){{"
                )
                transition_function.append(
                    f"\t\t\treturn {self.Q.index(self.d[self.Q[i]][letter])};"
                )
                transition_function.append("\t\t}")
            transition_function.append("\t}")
        transition_function.append("\texit(2);")
        transition_function.append("}")
        main_function = []
        main_function.extend([
            "int main(){",
            "\tint curr_state = 0;",
            "\tchar c;"
        ])
        len_state_names = max(map(lambda s: len(s), self.Q))
        main_function.append(
            f"\tchar state_names[{len(self.Q)}][{len_state_names + 1}] = {{"
        )
        for state in self.Q:
            main_function.append(
                f"\t\t\"{state}\","
            )
        main_function.append("\t};")
        main_function.extend([
            "\twhile((c = getchar())!=EOF && (c!='\\n')){",
            "\t\tcurr_state = transition(curr_state, c);",
            "\t\tprintf(\"%s\\n\", state_names[curr_state]);",
            "\t}"
        ])
        if len(self.F) != 0:
            temp = []
            for fstate in self.F:
                temp.append(
                    f"(curr_state == {self.Q.index(fstate)})"
                )
            if len(self.F) == 1:
                main_function.append(
                    f"\tif({temp[0]}){{"
                )
            else:
                main_function.append(
                    f"\tif ({temp[0]} ||"
                )
                for i in range(1, len(temp) - 1):
                    main_function.append(
                        f"\t   {temp[i]} ||"
                    )
                main_function.append(
                    f"\t    {temp[-1]}){{"
                )
            main_function.extend([
                "\t\tprintf(\"Accept\\n\");",
                "\t\treturn 0;",
                "\t}",
            ])
        main_function.extend([
            "\tprintf(\"Not Accept\\n\");",
            "\treturn 1;"
        ])
        main_function.append("}")
        lines = [*preprocessing, *transition_function, *main_function]
        return "\n".join(lines)

def check_consistency(alphabet, states, transition, q0, F):
    for state in states:
        if state not in transition:
            raise SemanticError(f"Semantic error: no transition specified for\
state {state}")
        for letter in alphabet:
            if letter not in transition[state]:
                raise SemanticError(f"Semantic error: no transition specified\
 for state {state} with character {letter}")
            if transition[state][letter] not in states:
                raise SemanticError(f"Semantic error: target state\
{transition[state][letter]} for initial state {state} with symbol {letter}\
invalid")
    if q0 not in states:
        raise SemanticError(f"Semantic error: initial state {q0} not in set of\
states")
    if not F.issubset(states):
        raise SemanticError("Semantic error: Invalid set of final states")

def constructDFA(source):
    source = source.strip()
    if source[0] != "{":
        raise SyntaxError("Syntax error: First character should be {")
    if source[-1] != "}":
        raise SyntaxError("Syntax error: Last character should be }")
    source = source[1:-1]
    if source.count(";") != 2:
        raise SyntaxError("Syntax error: Number of ; is not 2")
    segments = source.split(";")
    segments[0] = segments[0].strip()
    if not segments[0].isalnum():
        raise SyntaxError(f"Syntax error: Invalid start state {segments[0]}")
    segments[1] = segments[1].replace(" ", "").replace("\n", "").replace("\t", "")
    if segments[1] == '':
        final_states = set()
    else:
        final_states = set(segments[1].split(","))
    transitions = segments[2].split(",")
    alphabet = set()
    states = set()
    transition = dict()
    for rule in transitions:
        rule = rule.strip()
        if rule.count(" ") != 2:
            raise SyntaxError(f"Syntax error: {rule} - 3 tokens expected")
        tokens = rule.split(" ")
        for token in tokens:
            if not token.isalnum():
                raise SyntaxError(f"Syntax error: {token} - Unknown character")
        if len(tokens[1]) != 1:
            raise SyntaxError(f"Syntax error: {tokens[1]} - single character expected")
        states.update([tokens[0], tokens[2]])
        alphabet.update(tokens[1])
        if tokens[0] in transition:
            if tokens[1] in transition[tokens[0]]:
                raise SemanticError(f"Semantic error: {tokens[1]} appeared more than once for the same initial state")
            transition[tokens[0]][tokens[1]] = tokens[2]
        else:
            transition[tokens[0]] = dict()
            transition[tokens[0]][tokens[1]] = tokens[2]
    return DFA(states, alphabet, segments[0], transition, final_states)

if __name__ == "__main__":
    if len(sys.argv) != 4:
        sys.exit(USAGE)
    if not os.path.isfile(sys.argv[1]):
        sys.exit("Sourcefile not a valid filename")
    with open(sys.argv[1], 'r') as sourcefile:
        source = sourcefile.read()
    dfa = constructDFA(source)
    if sys.argv[2].endswith(".c"):
        c_code = dfa.compile_to_c()
        with open(sys.argv[2], "w") as outputfile:
            print(c_code, file=outputfile)
        print("C code written to " + sys.argv[2])
        try:
            subprocess.run(["gcc", sys.argv[2], "-o", sys.argv[3]])
        except FileNotFoundError:
            raise CompileError("GCC not found. Please ensure \"gcc\" is in path")
    elif sys.argv[2].endswith(".dot") and sys.argv[3].endswith(".png"):
        dot_code = dfa.compile_to_dot()
        with open(sys.argv[2], "w") as outputfile:
            print(dot_code, file=outputfile)
        print("DOT code written to " + sys.argv[2])
        try:
            subprocess.run(["dot", "-Tpng", sys.argv[2], "-o", sys.argv[3]])
        except FileNotFoundError:
            raise CompileError("DOT engine not found. Please ensure \"dot\" is in path")
    else:
        sys.exit(USAGE)
