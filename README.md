# SQL Plagarism Detector
### A Tool for Plagiarism Detection in SQL

SQL Plagiarism Detector is a tool designed to automatically mark answers as being potentially plagiarsed based on a number of methods. The tool compares every answer in the submission to every other answer (of the same question from a different student) and flags it as either potentially plagiarsed or not.

More details can be found in our paper - see below.

If you have any questions or problems, please email Anthony at a.kleerekoper@mmu.ac.uk

## Usage

Download the two python files and run SQLPlagiarismDetector, providing a CSV file as a command-line argument.

The input CSV file must contain three columns:

1. Student Numbers (ID numbers) - must be called "stu_num"
2. Question Numbers - must be called "ques_num"
3. Student Answers - must be called "answer"

The program saves the results in a new CSV file (named "output" with a timestamp) with each answer marked as either flagged or not. 

## Citing the Tool

You are free to adapt and modify SQL Plagiarism Detector. If you do so, please acknowledge us. If you use SQL Plagiarism Detector for research purposes, please cite the following paper:

*Kleerekoper, Anthony and Schofield, Andrew. "The False-Positive Rate of Automated Plagiarism Detection for SQL Assessments." Proceedings of the 2019 The UK and Ireland Computing Education Research Conference. ACM, 2019*

