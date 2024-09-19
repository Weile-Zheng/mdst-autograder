# MDST Autograder

## Criterias:

#### Checkpoint 0:

Checkpoint 0 are deterministic, so checkpoint 0's output will be compared with a solution. The output format must strictly match for the problem to be graded as correct. The output format will be clearly stated for each problem in checkpoint 0.

#### Checkpoint 1:

Few problems in checkpoint 1 are deterministic while most are non-deterministic. Since the tutorials are graded base on effort, we will not run a correctness test for non-deterministic problems.

For non-deterministic questions, we will simply check if code are present and runnable. If both passes, full score will be granted. If only code present but errors are thrown, then only half of the credits will be granted.

\*The methodology for grading checkpoint 1 is based on the assumption that it is unlikely students will input completely irrelavant code. If code are presented, the students have at least gave some effort on the problem.

## TODO

Frontend web interface:

-   Umich email collection
-   Tutorial files collection

Backend:

-   Result comparison for cp 0
-   Result comparison for deterministic cp1
-   Code check for non-deterministic cp1

Need:

-   Umich login or gmail login. If latter, have them provide umich email
-   Upload box for github repository
-   Upload box for tutorial 0, tutorial 1
-   Backend sql database for saving the application info
-   Tests are ran immediately when user submits.
