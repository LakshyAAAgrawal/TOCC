# TOCC
A software for Theory of Computation to convert NFA and DFA input as a custom language to:
1. C code which can read strings from stdin and show the series of transitions
   along with accept/reject status. It gets internally compiled using GCC.
2. DOT code which facilitates visualisation of the input NFA and DFA.
3. Conversion of NFA to DFA using [Powerset construction method](
   https://en.wikipedia.org/wiki/Powerset_construction)

## Usage
1. Pull the repository
   ```
   git clone https://github.com/LakshyAAAgrawal/TOCC
   ```
2. cd into the cloned repository
   ```
   cd TOCC
   ```
3. You could choose to install the software onto the system PATH or you could run directly.
### Installation
1. execute
   ```
   sudo ./install.sh
   ```
2. Run
   ```
   tocc sourcefile.dfa output.c output_binary   # Convert DFA to C and binary
   tocc sourcefile.dfa output.dot output.png    # Convert DFA to DOT and Image
   tocc sourcefile.nfa output.c output_binary   # Convert NFA to C and binary
   tocc sourcefile.nfa output.dot output.png    # Convert NFA to DOT and binary
   ```

### Without Installation
1. Run
   ```
   ./tocc.py sourcefile.dfa output.c output_binary   # Convert DFA to C and binary
   ./tocc.py sourcefuke.dfa output.dot output.png    # Convert DFA to DOT and Image
   ./tocc.py sourcefile.nfa output.c output_binary   # Convert NFA to C and binary
   ./tocc.py sourcefuke.nfa output.dot output.png    # Convert NFA to DOT and binary
   ```

## Language Specification
The custom language for DFA and NFA is specified as follows:
1. The names of states must be alphanumeric.
2. The program has the following structure:
   ```
   {
	   <Name of initial state>;
	   <Comma-separated names of final states>;
	   <state1> <symbol1> <state2>,
	   <state3> <symbol2> <state8>,
	   ...,
	   ...,
	   <statei> <symbolk> <statej>
   }
   ```
3. The ```<symbolk>``` above is a single alpha-numeric character specifying the symbol for making the transition from ```<statei>``` to ```<statej>```.
4. (Only for DFA) Corresponding to each state, transition rule must be specified for each letter of the alphabet.

## Example Language Code
1. The following DFA checks if the string over {0,1} contains even number of 1 or not:
	```
	{
		q0;
		q0;
		q0 0 q0,
		q0 1 q1,
		q1 0 q1,
		q1 1 q0
	}
	```
2. Save the above in "test.dfa"
3. Execute:
   ```
   tocc test.dfa test.c test
   tocc test.dfa test.dot test.png
   ```
4. C output:
   ```C
   #include<stdio.h>
   #include<stdlib.h>
   int transition(int q, char b){
	   if(q == 0){
		   if(b == '0'){
			   return 0;
		   }
		   if(b == '1'){
			   return 1;
		   }
	   }
	   if(q == 1){
		   if(b == '0'){
			   return 1;
		   }
		   if(b == '1'){
			   return 0;
		   }
	   }
	   exit(2);
   }
   int main(){
	   int curr_state = 0;
	   char c;
	   char state_names[2][3] = {
		   "q0",
		   "q1",
	   };
	   while((c = getchar())!=EOF && (c!='\n')){
		   curr_state = transition(curr_state, c);
		   printf("%s\n", state_names[curr_state]);
	   }
	   if((curr_state == 0)){
		   printf("Accept\n");
		   return 0;
	   }
	   printf("Not Accept\n");
	   return 1;
   }
   ```
   DOT output
   ```dot
   digraph DFA{
	   q0 [shape="doublecircle"]
	   q1 [shape="circle"]
	   __ [label="", fixedsize="false", width=0, height=0, shape=none]
	   q0 -> q0 [label="0"]
	   q0 -> q1 [label="1"]
	   q1 -> q1 [label="0"]
	   q1 -> q0 [label="1"]
	   __ -> q0
   }
   ```
   ![DFA](https://i.imgur.com/v9PH3ld.png)
5. Test 1
   ```
   echo "01" | ./test
   ```
   Output
   ```
   q0
   q1
   Not Accept
   ```
   Test 2
   ```
   echo "011" | ./test
   ```
   Output
   ```
   q0
   q1
   q0
   Accept
   ```
