def program():
    print("""
    STQA
          1. testplan
          2. testcase
          3. testcasesra
          4. blackboxtesting
          5. whiteboxtesting
          6. defectreport
          7. seleniumtesting
          8. postmanwinrunnertesting
""")

def testplan():
    print("""
Ass 1
Title:
Test Plan for Windows Paint / Windows Calculator

Objective:
The main objective of this test plan is to define the strategy, scope, approach, and schedule of the testing activities for the Windows Paint or Windows Calculator application.
The purpose is to ensure that the application functions correctly, meets user requirements, and provides a reliable and user-friendly interface without errors or crashes.

Theory:
A Test Plan is a detailed document that outlines the testing strategy, objectives, schedule, estimation, deliverables, and resources required to validate the quality of a software application. It serves as a blueprint for systematically verifying that the software product meets its specified requirements.
Key Components of a Test Plan:
1.Test Objectives: Defines what needs to be achieved through testing (e.g., validating functionalities, ensuring reliability).
2.Scope: Describes the features and functionalities to be tested and not to be tested.
3.Test Environment: Specifies the hardware, software, and tools required for testing.
4.Test Strategy: Outlines the methods of testing (manual/automated, functional/non-functional).
5.Test Cases: Define specific inputs, execution conditions, and expected results.
6.Test Schedule: Specifies the testing timeline.
7.Deliverables: Includes test reports, defect logs, and summary documents.
Importance of a Test Plan:
Ensures systematic testing of all modules.
Helps in identifying defects early.
Provides a clear roadmap for the testing team.
Ensures software reliability and performance.

Scope of Testing:
For Windows Paint:
Drawing shapes, lines, and using color tools.
Saving and opening image files.
Undo and redo operations.
Clipboard operations (cut, copy, paste).
Zoom in/out, resize, rotate image functionalities.
For Windows Calculator:
Performing basic arithmetic operations (addition, subtraction, multiplication, division).
Checking memory functions (M+, M-, MR, MC).
Using advanced functions (square root, percentage, etc.).
Verifying keyboard input support.
Testing error handling (e.g., division by zero).

Test Environment:
Component           	Specification
Operating System	    Windows 10 / Windows 11
Hardware             	Intel i5 or higher, 8 GB RAM
Tools Used	          Manual Testing, Defect Tracking Sheet (Excel / Bugzilla)
Tester	              QA Analyst

Test Strategy:
Type of Testing: Functional, Usability, Regression, and GUI Testing
Testing Method: Manual Testing
Test Data: User inputs (numbers, operations, image file names, etc.)
Entry Criteria: Application is installed and ready to test
Exit Criteria: All planned test cases are executed and major bugs are resolved

Test Cases Table (Example)
Test Cases for Windows Paint
Test Case ID	 Test Scenario	          Test Steps	                             Expected Result	                    Actual Result	Status (Pass/Fail)
TC01	         Open Paint Application	  Click on Paint icon from Start menu	     Paint window opens successfully		
TC02         	 Draw a Line	            Select “Line” tool and draw on canvas	   Straight line is drawn correctly		
TC03	         Change Color	            Select a color from palette and draw	   Drawing appears in selected color		
TC04	         Save File	              File → Save As → JPEG	                   File saves successfully		
TC05	         Undo Action	            Draw and press “Ctrl + Z”	               Last action undone successfully		

Test Cases for Windows Calculator
Test Case ID	Test Scenario	Test Steps	Expected Result	Actual Result	Status (Pass/Fail)
TC01	Launch Calculator	Click on Calculator from Start menu	Calculator opens successfully		
TC02	Addition	Enter 5 + 7	Output displayed as 12		
TC03	Division by Zero	Enter 5 ÷ 0	Displays “Cannot divide by zero”		
TC04	Memory Function	Use M+ and MR operations	Stored value retrieved correctly		
TC05	Clear Operation	Enter numbers and click “C”	Display clears to 0		

Defect Reporting Table (Sample)
Defect ID	Module	Description	Severity	Status	Tester
D01	Calculator	Application crashes when dividing large numbers	High	Open	QA Tester
D02	Paint	Undo fails after more than 10 actions	Medium	Closed	QA Tester

Deliverables:
Test Plan Document
Test Cases Document
Defect Report
Test Summary Report

Conclusion:
This test plan provides a structured approach to verify the functionality, usability, and stability of the Windows Paint / Windows Calculator application.
By executing all defined test cases and resolving the identified defects, we can ensure that the application meets user expectations and performs reliably under different scenarios.
The results of this testing will help improve software quality and user satisfaction.

""")
    

def testcase():
    print("""
Ass 2
Title:
Test Plan for an E-Commerce Website / Mobile Shopping Application

Objective:
The main objective of this test plan is to outline the testing strategy, scope, resources, schedule, and deliverables required for testing an E-Commerce website or mobile shopping application.
The goal is to ensure that all website features — including product search, cart management, checkout, and payment — work correctly, efficiently, and provide a seamless experience to users across devices.

Theory:
A Test Plan is a detailed document that describes the testing approach to verify and validate that a software system meets its functional and non-functional requirements.
It acts as a roadmap for testing and helps ensure that all modules are verified systematically before release.
Key Elements of a Test Plan:
1.Test Objective: Defines what is to be tested and why.
2.Scope: Features to be tested and excluded.
3.Test Environment: Software, hardware, tools, and data needed for testing.
4.Test Strategy: Types of testing (Functional, UI, Usability, Performance, etc.).
5.Test Cases: Step-by-step scenarios for validation.
6.Defect Management: Recording and tracking of bugs.
7.Deliverables: Test reports and metrics.
Importance of a Test Plan:
Ensures comprehensive coverage of all functionalities.
Helps in identifying and fixing defects early.
Acts as a communication tool between developers and testers.
Guarantees software reliability and usability.




Scope of Testing:
Features to be Tested:
User Registration and Login
Product Search and Filtering
Add to Cart and Checkout Process
Payment Gateway Integration
Order Confirmation and Tracking
Responsive Design (for different devices)
Features Not in Scope:
Backend database performance optimization
Third-party analytics integrations

Test Environment:
Component	Description
Application Type	Web / Mobile App
Operating System	Windows 10, Android 13, iOS 17
Browser	Chrome, Edge, Firefox, Safari
Tools Used	Manual Testing, Excel for Test Cases, Jira/Bugzilla for Defect Tracking
Tester	QA Engineer

Test Strategy:
Testing Type	Description
Functional Testing	Verify that all features like login, search, and payment work correctly.
Usability Testing	Check ease of navigation, button placement, and design clarity.
Performance Testing	Validate response time and page load speed.
Security Testing	Check login security and payment data protection.
Compatibility Testing	Test across browsers and mobile devices.
Regression Testing	Ensure new updates do not affect existing features.




Test Cases Table
Test Case ID	Module	Test Scenario	Test Steps	Expected Result	Actual Result	Status (Pass/Fail)
TC01	Login	Verify user login with valid credentials	Enter valid email & password, click Login	User successfully logs in		
TC02	Login	Verify login with invalid password	Enter invalid password	Error message displayed		
TC03	Product Search	Search product by name	Enter product keyword and click search	Relevant products displayed		
TC04	Cart	Add item to cart	Click “Add to Cart” button	Item appears in cart		
TC05	Checkout	Place order with valid card	Enter card details and confirm order	Order confirmation page displayed		
TC06	Payment	Test invalid card details	Enter wrong card info	Payment fails with proper message		

Defect Reporting Table
Defect ID	Module	Description	Severity	Status	Tester
D01	Login	App crashes when login credentials are blank	High	Open	QA Tester
D02	Checkout	Payment confirmation email not sent	Medium	In Progress	QA Tester
D03	Search	Product image not loading on mobile	Low	Closed	QA Tester

Test Schedule:
Phase	Start Date	End Date	Activities
Test Planning	01-Nov-2025	02-Nov-2025	Prepare test plan and environment setup
Test Case Design	03-Nov-2025	05-Nov-2025	Write and review test cases
Test Execution	06-Nov-2025	10-Nov-2025	Execute test cases and report defects
Retesting & Closure	11-Nov-2025	12-Nov-2025	Verify fixes and close report

Deliverables:
Test Plan Document
Test Case Sheet (Excel)
Bug Report Document
Test Summary Report

Conclusion:
The test plan defines the complete strategy to ensure the e-commerce website or mobile application functions as intended.
By systematically executing and tracking test cases, we can verify that critical features such as login, search, payment, and checkout are free from major defects.
Effective testing increases user satisfaction, reliability, and the overall quality of the final product before deployment.
""")
    

def testcasesra():
    print("""
Ass 2
Title:
Test Case Report for Student Result Analyzer Web Application

Objective:
The objective of this test case report is to document the results of the testing process for the Student Result Analyzer web application.
This report aims to ensure that all functionalities — such as uploading PDF ledgers, analyzing student results, and displaying top performers — are tested and validated to confirm that the system works accurately and efficiently.

Theory:
A Test Case Report is a structured document that records the outcome of executing test cases. It helps track the testing process, identify issues, and verify whether the software meets the desired quality standards.
Purpose of Test Case Report:
1.To summarize test execution results.
2.To ensure all features were tested as per the test plan.
3.To document any detected defects or deviations.
4.To support developers and stakeholders in improving software reliability.
Essential Components:
Test Case ID: Unique identifier for each test case.
Module Name: Area or feature being tested.
Test Scenario & Steps: Describes what is being tested and how.
Expected Result vs. Actual Result: Comparison of intended behavior with observed output.
Status: Indicates whether the test passed or failed.
Remarks / Defect ID: Additional notes or bug references.

Scope of Testing:
Modules Tested:
1.PDF Upload Module
2.Result Extraction Module
3.Top 5 Students Display
4.Subject-wise Analysis
5.Class-wise Graphical Analysis

Test Case Report Table
Test Case ID	Module Name	Test Scenario	Test Steps	Expected Result	Actual Result	Status (Pass/Fail)	Remarks / Defect ID
TC01	PDF Upload	Verify valid PDF upload	Upload correct university ledger file	File uploaded successfully	Works as expected	Pass	-
TC02	PDF Upload	Upload invalid file format	Try uploading .docx file	System shows invalid file format message	Message displayed	Pass	-
TC03	Result Extraction	Extract student data	Click “Analyze” after upload	Student data extracted correctly	Some rows missing	Fail	D01
TC04	Top Students	Display top 5 students	Click on “Top 5 Students” tab	Correct top 5 students displayed	Correct output	Pass	-
TC05	Subject Analysis	Analyze subject performance	Click on “Subject Analysis”	Bar chart displayed with subject averages	Chart displayed accurately	Pass	-
TC06	Class Analysis	View overall performance	Open “Class Analysis” section	Pie chart of pass/fail ratio shown	Works correctly	Pass	-
TC07	Error Handling	Check missing data scenario	Upload incomplete ledger	Application handles gracefully	App crashes	Fail	D02
TC08	UI & Navigation	Verify responsive layout	Open on mobile browser	Interface adjusts properly	Works fine	Pass	-



Defect Summary Table
Defect ID	Module	Description	Severity	Status	Tester
D01	Result Extraction	Some student rows missing during extraction	High	Open	QA Tester
D02	Error Handling	App crashes on incomplete ledger upload	High	In Progress	QA Tester

Test Execution Summary
Total Test Cases	Passed	Failed	Blocked	Pass Percentage
8	6	2	0	75%

Conclusion:
The testing of the Student Result Analyzer web application verified most core functionalities, including file upload, result extraction, and performance visualization.
While 75% of test cases passed successfully, a few defects related to data extraction and error handling need resolution.
After fixing these defects and conducting regression testing, the system will be ready for stable deployment.

""")
    

def blackboxtesting():
    print("""
Ass 3
Title:
Manipulation and Implementation of Black Box Testing Methods for Student Result Analyzer

Objective:
The objective of this assignment is to apply and analyze various Black Box Testing Techniques — such as Positive & Negative Testing, Equivalence Partitioning, and Boundary Value Analysis (BVA) — on the Student Result Analyzer project.
This helps in verifying that all modules of the system behave as expected when tested with valid and invalid inputs, and ensures the overall reliability and correctness of the software.

Theory:
Black Box Testing is a software testing technique in which the internal structure or code of the application is not known to the tester. The testing focuses only on the inputs and the expected outputs of the software system.
It is also known as Behavioral Testing, where the emphasis lies on checking the functionality rather than the implementation.
Key Characteristics:
Testers are unaware of the internal logic or structure.
Based purely on functional specifications or requirements.
Input → Processing → Output model is tested.
Commonly used during System Testing and Acceptance Testing.

1️⃣ Positive Testing and Negative Testing
Theory:
Positive Testing: Checks how the system behaves with valid input to verify that it produces the expected result.
Negative Testing: Checks how the system behaves with invalid, unexpected, or incorrect input, ensuring the software handles errors gracefully without crashing.

Example (Module: PDF Upload & Result Extraction):
Test Case ID	Test Type	Input	Expected Output	Actual Output	Status
TC01	Positive	Upload valid university result PDF file	File uploaded and processed successfully	Works correctly	Pass
TC02	Positive	Click “Analyze Results” after valid file upload	Student data extracted and displayed	Works correctly	Pass
TC03	Negative	Upload an unsupported file (.docx, .txt)	System shows “Invalid file format” message	Works correctly	Pass
TC04	Negative	Upload empty PDF file	Application should show “File is empty”	System shows error	Pass
TC05	Negative	Analyze without uploading any file	System displays “No file uploaded”	Works correctly	Pass
✅ Observation:
Both valid and invalid inputs were handled correctly. No unexpected crashes were observed.

2️⃣ Equivalence Partitioning (EP)
Theory:
Equivalence Partitioning divides input data into different partitions or classes where test cases can be designed to cover each partition.
Each partition represents a group of inputs that are expected to be treated similarly by the system.
Example (Module: Marks Input Validation for Analysis):
Suppose the Student Result Analyzer accepts marks between 0 to 100 for analysis.
Input Condition	Partition Type	Valid Range / Class	Representative Value	Expected Output	Result
Marks < 0	Invalid Partition	Negative numbers	-5	Show error “Invalid marks”	Pass
Marks between 0–100	Valid Partition	Acceptable marks range	85	Marks processed successfully	Pass
Marks > 100	Invalid Partition	Greater than maximum	105	Show error “Marks exceed limit”	Pass
Marks = Null	Invalid Partition	Empty input	Null	Show error “Marks required”	Pass
✅ Observation:
The system correctly accepts only valid marks (0–100) and rejects all other partitions with appropriate error messages.

3️⃣ Boundary Value Analysis (BVA)
Theory:
Boundary Value Analysis is based on the principle that errors are most likely to occur at the boundaries of input ranges rather than within the middle values.
Test cases are created for boundary conditions — minimum, just below minimum, nominal, just above maximum, and maximum values.
Example (Module: Marks Validation):
Allowed marks range: 0 – 100
Test Case ID	Input Value (Marks)	Boundary Type	Expected Output	Actual Output	Status
TC01	-1	Below Lower Boundary	Invalid marks error	Error displayed	Pass
TC02	0	Exact Lower Boundary	Accept marks	Accepted	Pass
TC03	1	Just Above Lower Boundary	Accept marks	Accepted	Pass
TC04	99	Just Below Upper Boundary	Accept marks	Accepted	Pass
TC05	100	Exact Upper Boundary	Accept marks	Accepted	Pass
TC06	101	Above Upper Boundary	Invalid marks error	Error displayed	Pass
✅ Observation:
The system correctly identifies the valid boundaries (0–100) and rejects values outside the range.

4️⃣ Summary of Testing Results
Technique	Test Area	Total Test Cases	Passed	Failed	Pass %
Positive/Negative Testing	PDF Upload, Result Extraction	5	5	0	100%
Equivalence Partitioning	Marks Validation	4	4	0	100%
Boundary Value Analysis	Marks Validation	6	6	0	100%
✅ Overall Pass Rate: 100%

Conclusion:
By implementing Black Box Testing Methods — including Positive & Negative Testing, Equivalence Partitioning, and Boundary Value Analysis — on the Student Result Analyzer project, all functional modules were verified effectively.
The testing ensured that the application:
Handles valid and invalid inputs correctly,
Maintains input validation boundaries accurately, and
Provides stable and error-free behavior across modules.
This structured testing approach improved the overall software reliability, data accuracy, and user satisfaction of the Student Result Analyzer system.

""")
  

def whiteboxtesting():
    print("""
Ass 4
Title:
Manual Implementation of White Box Testing Methods for Student Result Analyzer Project

Objective:
The objective of this assignment is to analyze and manually implement White Box Testing techniques — including Statement Coverage, Branch Coverage, and Path Coverage — on a selected portion of the Student Result Analyzer project’s source code.
This helps ensure that every possible logical path and condition within the code is tested and verified for correctness.

Theory:
White Box Testing is a testing technique that examines the internal structure, logic, and code implementation of a software program.
Unlike Black Box Testing, which focuses on system behavior, White Box Testing checks how the system performs its functions by testing internal logic, decision points, loops, and statements.
Common White Box Testing Methods:
1.Statement Coverage – Ensures every executable statement in the code is executed at least once.
2.Branch Coverage – Ensures every decision (if-else, switch) takes both true and false outcomes.
3.Path Coverage – Ensures every possible path through the code is executed at least once.
Importance:
Helps detect logical and runtime errors early.
Ensures thorough coverage of program logic.
Improves code reliability and performance.

Sample Code (from Student Result Analyzer Project):
Below is a simplified Python function used to analyze student grades in your project:
def calculate_grade(percentage):
    if percentage < 0 or percentage > 100:
        return "Invalid"
    elif percentage >= 75:
        return "Distinction"
    elif percentage >= 60:
        return "First Class"
    elif percentage >= 40:
        return "Pass"
    else:
        return "Fail"
This function determines the grade of a student based on their percentage marks.

1️⃣ Statement Coverage
Theory:
Statement Coverage ensures that every line of code is executed at least once during testing.
It helps confirm that no statement remains untested in the code.
Implementation Steps:
Identify all statements in the function.
Create minimum test cases that execute all statements at least once.
Total Executable Statements: 6
(Each if, elif, else, and return counts as one statement.)
Test Case Table (Statement Coverage)
Test Case ID	Input (Percentage)	Expected Output	Executed Statements	Coverage Achieved
TC1	85	Distinction	if (false), elif (true) → return “Distinction”	4/6
TC2	65	First Class	elif (true) → return “First Class”	5/6
TC3	35	Fail	elif, else → return “Fail”	6/6
✅ Result: 100% Statement Coverage Achieved.

2️⃣ Branch Coverage
Theory:
Branch Coverage ensures that each decision or condition in the code executes both True and False outcomes at least once.
Implementation Steps:
Identify all decision points (if, elif, else).
Create test cases so that each condition evaluates both ways.
Decision Points in Code: 4
(1 if, 3 elif)
Test Case Table (Branch Coverage)
Test Case ID	Input	Condition Evaluated	True/False Outcome	Output
TC1	-5	percentage < 0 → True	True	Invalid
TC2	85	percentage >= 75 → True	True	Distinction
TC3	65	percentage >= 60 → True	True	First Class
TC4	45	percentage >= 40 → True	True	Pass
TC5	20	All above False	False	Fail
✅ Result:
All branches (True/False) of every decision are covered → 100% Branch Coverage Achieved.

3️⃣ Path Coverage
Theory:
Path Coverage ensures that every possible route (path) through a program is executed at least once.
Each path corresponds to a unique combination of conditions being true or false.
Implementation Steps:
Identify all possible logical paths through the code.
Create test cases to execute each path.
Possible Paths in Code:
1.Path 1: Invalid Input → "Invalid"
2.Path 2: Valid ≥ 75 → "Distinction"
3.Path 3: Valid between 60–74 → "First Class"
4.Path 4: Valid between 40–59 → "Pass"
5.Path 5: Valid < 40 → "Fail"
Test Case Table (Path Coverage)
Path ID	Condition Flow	Input Value	Expected Output
P1	percentage < 0 or > 100	-5	Invalid
P2	percentage ≥ 75	85	Distinction
P3	percentage ≥ 60	65	First Class
P4	percentage ≥ 40	50	Pass
P5	percentage < 40	20	Fail
✅ Result:
All 5 possible paths have been executed → 100% Path Coverage Achieved.

4️⃣ Coverage Summary
Testing Type	Goal	Total Test Cases	Coverage Achieved
Statement Coverage	Execute every statement	3	100%
Branch Coverage	Execute all true/false branches	5	100%
Path Coverage	Execute every unique path	5	100%
✅ Overall Result: Full coverage achieved with 5 unique inputs.

Conclusion:
Through manual implementation of White Box Testing Methods — Statement Coverage, Branch Coverage, and Path Coverage — on the Student Result Analyzer project code, we verified that:
All logical paths, decisions, and statements are covered and tested.
The system correctly handles boundary and invalid values.
Code execution flow is logically consistent and error-free.
This testing confirms that the grading module in the Student Result Analyzer is robust, reliable, and functionally correct.
White Box Testing thus ensures deeper code-level quality and helps in improving software performance and accuracy.

""")
    

def defectreport():
    print("""
Ass 5
Title:
Preparation of Defect Report for Student Result Analyzer Project Using Excel

Objective:
The main objective of this assignment is to record, track, and analyze defects identified during the testing phase of the Student Result Analyzer project.
A Defect Report provides complete information about issues or errors discovered after the execution of test cases, including their severity, status, assigned developer, and resolution progress.
It ensures systematic management of defects and improves software quality through timely corrections.

Theory:
A Defect Report (also called a Bug Report) is a formal document used in software testing to log and monitor any deviation of the system from its expected behavior.
When test cases are executed, if the actual result differs from the expected result, a defect is raised.
Key Components of a Defect Report:
1.Defect ID: Unique number assigned to each defect for easy tracking.
2.Module/Feature Name: Specifies where the defect occurred.
3.Test Case ID: Links the defect to the corresponding test case.
4.Description: Brief explanation of the issue found.
5.Steps to Reproduce: Clear, repeatable steps to reproduce the issue.
6.Expected Result: Correct behavior of the system.
7.Actual Result: Observed incorrect behavior.
8.Severity: Impact of the defect (Critical, Major, Minor, Low).
9.Priority: Order in which the defect should be fixed (High, Medium, Low).
10.Status: Indicates whether the bug is Open, In Progress, Fixed, or Closed.
11.Reported By / Assigned To: Who raised the defect and to whom it is assigned for resolution.
12.Date Reported / Date Closed: Helps track defect resolution time.

Project Description:
Student Result Analyzer is a web-based application that analyzes PDF ledger reports from the university and generates:
Top 5 Students List
Subject-wise Analysis
Class-wise Performance Charts
During testing, a few functional and UI-related defects were found after executing the test cases.

🧮 Defect Report Table (Excel Format)
Below is the structured format of the Defect Report that would be created in Excel:
Defect ID	Module Name	Test Case ID	Description of Defect	Steps to Reproduce	Expected Result	Actual Result	Severity	Priority	Status	Reported By	Assigned To	Date Reported	Date Closed
D001	PDF Upload	TC_01	Upload fails for large PDF files (>10MB).	Select PDF >10MB and click upload.	File should upload successfully.	System shows “Upload Failed” error.	Major	High	Open	Tester1	Dev1	01-Nov-2025	—
D002	Result Parser	TC_03	Incorrect marks extraction for subjects with two-word names.	Upload sample ledger file with “Computer Networks” subject.	Marks should display correctly.	Marks displayed as zero.	Critical	High	In Progress	Tester2	Dev2	01-Nov-2025	—
D003	Student Ranking	TC_05	Top 5 list shows duplicate entries.	Run analysis for class “TYBSc-IT”.	Each student should appear only once.	Duplicate entries appear in list.	Major	Medium	Open	Tester1	Dev3	01-Nov-2025	—
D004	Chart Generation	TC_07	Pie chart labels overlap for small datasets.	Generate chart with 3 subjects.	Labels should be readable.	Labels overlap visually.	Minor	Low	Fixed	Tester3	Dev1	30-Oct-2025	31-Oct-2025
D005	UI Dashboard	TC_09	Text misalignment in student performance table.	Open class performance dashboard.	Columns should align properly.	Columns appear shifted.	Minor	Low	Closed	Tester2	Dev2	25-Oct-2025	28-Oct-2025

Analysis of Defects:
Severity Level	Count	Examples
Critical	1	D002 (Marks Extraction Issue)
Major	2	D001 (Upload Issue), D003 (Duplicate Ranking)
Minor	2	D004 (Chart Label Overlap), D005 (UI Misalignment)
Observation:
Total Defects Found: 5
Critical & Major Issues: 3
Minor UI Issues: 2
1 defect resolved and closed, 1 fixed, and 3 currently open.

Defect Status Summary
Status	Count
Open	2
In Progress	1
Fixed	1
Closed	1
✅ Current Resolution Rate: 40%
(2 out of 5 defects resolved)

Defect Lifecycle in the Project:
1.New: Defect identified after test execution.
2.Open: Assigned to developer for fixing.
3.In Progress: Developer currently working on the defect.
4.Fixed: Developer resolved the defect and submitted for re-testing.
5.Closed: Tester verified fix and confirmed issue is resolved.

Advantages of Maintaining Defect Report:
Enables better tracking of software quality across versions.
Facilitates efficient communication between testers and developers.
Helps prioritize and manage fixes effectively.
Provides a historical record of quality issues and resolutions.

Conclusion:
The Defect Report created in Excel for the Student Result Analyzer project provides a clear, structured view of all issues raised after executing test cases.
By categorizing defects based on severity, priority, and status, the testing team ensured that critical bugs were addressed first, and progress was measurable.
Such systematic defect reporting enhances the overall quality assurance process and ensures that the final software product is stable, reliable, and user-friendly before deployment.

""")
    

def seleniumtesting():
    print("""
Ass 6
Title:
Study and Implementation of Selenium Testing Tool for Student Result Analyzer Project

Objective:
The objective of this assignment is to study Selenium as an automated testing tool and understand how it can be used to test the Student Result Analyzer web application.
This includes analyzing Selenium’s features, architecture, components, and applying it to perform functional and regression testing of the project’s modules like PDF upload, result analysis, and report generation.

Theory:
🔹 Introduction to Selenium
Selenium is an open-source automated testing framework used for testing web-based applications. It enables testers and developers to write test scripts that simulate user actions on web browsers, ensuring that web pages and web applications behave as expected.
Selenium supports multiple programming languages such as Python, Java, C#, Ruby, JavaScript, and is compatible with browsers like Chrome, Edge, Firefox, Safari, and Opera.
It is primarily used for functional testing, regression testing, and cross-browser testing.

🔹 Need for Selenium in Project Testing
In your Student Result Analyzer project, which is a Flask-based web application, manual testing ensures correctness but is time-consuming for repetitive test cases.
Using Selenium automates:
Uploading PDF result ledgers.
Verifying extracted student data.
Checking top 5 student rankings.
Generating and validating performance charts.
Ensuring UI responsiveness across browsers.
This saves time, improves accuracy, and supports continuous integration testing.

Components of Selenium Suite:
Component	Description	Use in Project
Selenium IDE	Record-and-playback tool for creating quick scripts.	Used to record simple test flows like login, PDF upload.
Selenium WebDriver	Core API for browser automation using real browsers.	Used for automated testing of upload, result analysis, and UI elements.
Selenium Grid	Enables parallel test execution across multiple systems/browsers.	Used for cross-browser testing of Student Result Analyzer.
Selenium RC (Deprecated)	Older version used for server-based automation.	Not used (replaced by WebDriver).

Selenium Architecture Overview
Selenium follows a Client–Server Architecture:
1.Selenium Client Libraries – Contain APIs for supported programming languages (Python/Java).
2.JSON Wire Protocol – Acts as a communication bridge between client libraries and the WebDriver.
3.Browser Drivers – Specific to each browser (ChromeDriver, GeckoDriver, etc.).
4.Browsers – The web browsers where tests are executed.

Selenium WebDriver Implementation (Python Example)
Below is a sample code snippet for your Student Result Analyzer project, used to automate testing of the PDF upload and analysis feature:
from selenium import webdriver
from selenium.webdriver.common.by import By
import time

# Initialize Chrome WebDriver
driver = webdriver.Chrome()

# Open the Student Result Analyzer web app
driver.get("http://127.0.0.1:5000")

# Upload PDF test file
upload_button = driver.find_element(By.ID, "pdfUpload")
upload_button.send_keys("C:\\Users\\Test\\sample_result.pdf")

# Submit for analysis
driver.find_element(By.ID, "analyzeButton").click()
time.sleep(3)

# Verify the success message
result = driver.find_element(By.ID, "successMessage").text

if "Analysis Complete" in result:
    print("Test Passed: PDF analyzed successfully!")
else:
    print("Test Failed: Analysis not completed.")

driver.quit()
This script automates:
Opening the web application
Uploading a PDF
Executing analysis
Checking if the “Analysis Complete” message appears

Advantages of Using Selenium
Feature	Description
Open Source	Free and community-supported.
Cross-Browser Compatibility	Works on Chrome, Firefox, Edge, etc.
Multiple Language Support	Supports Python, Java, C#, Ruby.
Integration with CI/CD	Works with Jenkins, GitHub Actions, etc.
Parallel Execution	Supports running tests across multiple browsers simultaneously.
High Accuracy	Reduces human error compared to manual testing.





Disadvantages / Limitations
Limitation	Explanation
No support for desktop applications	Selenium only tests web-based systems.
Requires technical knowledge	Testers must know coding and browser drivers.
Dynamic elements handling	AJAX and dynamic UI testing can be complex.
Maintenance overhead	Script updates are needed when the UI changes.

Sample Test Case Table (Automated via Selenium)
Test Case ID	Test Scenario	Test Steps	Expected Result	Actual Result	Status
TC_01	Verify PDF upload functionality	Upload sample ledger PDF	PDF uploaded successfully	PDF uploaded successfully	Pass
TC_02	Verify “Analyze Result” button click	Click Analyze button	Analysis completed message appears	Message appeared	Pass
TC_03	Verify incorrect file format upload	Upload .txt file	Error message shown	Error message shown	Pass
TC_04	Verify student ranking list	Run analysis and view top 5	Top 5 students displayed correctly	Display correct	Pass
TC_05	Verify responsive UI	Resize window	Layout adjusts automatically	Adjusted correctly	Pass



Result Summary Table
Total Test Cases	Passed	Failed	Pass Percentage
5	5	0	100%
✅ The Selenium test automation achieved 100% success in the tested modules.

Conclusion:
The study and implementation of Selenium Testing Tool for the Student Result Analyzer project demonstrated how automation significantly improves testing efficiency, reliability, and repeatability.
Selenium successfully validated major functionalities like PDF upload, result processing, and UI responsiveness, ensuring that the system performs as expected across browsers.
Through Selenium automation, repetitive manual testing was replaced by faster, script-driven testing, leading to improved accuracy and reduced human error.
Hence, Selenium proves to be an essential tool for modern web application testing and continuous integration in software development.

""")
    

def postmanwinrunnertesting():
    print("""
Ass 7
Title:
Study of Postman and WinRunner Testing Tools with Simulation on Student Result Analyzer Project

Objective:
The main objective of this assignment is to study and understand the working of Postman and WinRunner testing tools, and to simulate software testing operations on the Student Result Analyzer project.
This involves exploring how these tools assist in API Testing (Postman) and Functional GUI Testing (WinRunner), and observing their role in improving test efficiency, accuracy, and automation within the software development process.

Theory:
Software testing tools are designed to automate and streamline the testing process. Among these tools, Postman and WinRunner are widely used for different purposes.

1️⃣ Postman Testing Tool
Introduction:
Postman is an API testing tool that allows developers and testers to send, receive, and validate requests and responses between a client and a server.
It is commonly used in RESTful API testing and integration testing of web applications.
In the Student Result Analyzer project, Postman is used to test the backend API endpoints built in Flask that handle:
PDF upload
Student data extraction
Result analysis and chart generation

Features of Postman:
Feature	Description
User-Friendly Interface	Allows sending HTTP requests easily using GUI.
Supports Multiple Methods	GET, POST, PUT, DELETE, PATCH.
Automation via Collections	Group multiple test cases for continuous testing.
Scripting Support	JavaScript-based scripting for automated response validation.
Environment Variables	Reusable parameters for different environments (dev, test, prod).
Integration	Works with Jenkins, Newman, and CI/CD pipelines.

Simulation of Testing in Postman (On Your Project):
API Endpoint	Method	Purpose	Request Type	Expected Response
/upload	POST	Upload student result PDF	Multipart File	200 OK – “File uploaded successfully”
/analyze	GET	Trigger analysis of uploaded data	JSON	JSON output with grades & summary
/top_students	GET	Fetch top 5 students	JSON	JSON array with student names & marks
/class_summary	GET	Class-wise average and performance	JSON	Chart data in JSON format

Example Test in Postman:
Endpoint:
http://127.0.0.1:5000/top_students
Request Method:
GET
Expected Response (JSON):
[
  {"name": "Amit Patil", "percentage": 89.4},
  {"name": "Nisha Kulkarni", "percentage": 87.1},
  {"name": "Rahul Joshi", "percentage": 86.8},
  {"name": "Sneha Rao", "percentage": 85.3},
  {"name": "Pooja Deshmukh", "percentage": 84.7}
]
Validation Script in Postman:
pm.test("Status code is 200", function () {
    pm.response.to.have.status(200);
});

pm.test("Response contains 5 students", function () {
    var jsonData = pm.response.json();
    pm.expect(jsonData.length).to.eql(5);
});
✅ Result: All API test cases passed successfully.




2️⃣ WinRunner Testing Tool
Introduction:
WinRunner is a Functional GUI Testing Tool developed by Mercury Interactive (now part of Micro Focus).
It is designed to automate the process of testing GUI-based applications by recording, replaying, and verifying user interactions with the application interface.
Although WinRunner primarily supports desktop applications, its principles can be simulated for web UI validation in the Student Result Analyzer project.

Features of WinRunner:
Feature	Description
Record and Playback	Captures user actions and replays them for testing.
TSL (Test Script Language)	Proprietary scripting for advanced test scenarios.
GUI Map Editor	Identifies and stores objects (buttons, fields, links) in the application.
Data-Driven Testing	Executes tests with multiple input datasets.
Integration with TestDirector	Enables test management and defect tracking.

Simulation of WinRunner on Your Project:
Scenario: Validate that after uploading a PDF file, the analysis result table and charts display correctly.
Step No.	Action	Expected Result	Actual Result	Status
1	Launch the Student Result Analyzer web app	Application homepage opens	Homepage displayed	Pass
2	Click on “Upload PDF” button	File upload dialog appears	Dialog displayed	Pass
3	Select a valid PDF file and click “Upload”	PDF uploaded successfully	Upload confirmed	Pass
4	Click on “Analyze” button	Analysis completes, table appears	Results table generated	Pass
5	Verify chart section	Charts generated and visible	Charts displayed properly	Pass
✅ Simulation Result: All 5 GUI actions executed successfully, mimicking WinRunner functionality.

Comparison Between Postman and WinRunner
Parameter	Postman	WinRunner
Testing Type	API Testing	GUI Functional Testing
Platform	Web / REST APIs	Desktop / Web UI
Automation Script Language	JavaScript	TSL (Test Script Language)
Integration	Jenkins, CI/CD tools	TestDirector, Quality Center
Use in Project	Testing Flask API endpoints	Testing front-end UI components
Ease of Use	High (modern tool)	Moderate (legacy tool)

Results Summary
Tool Used	Test Cases Executed	Passed	Failed	Success Rate
Postman	4	4	0	100%
WinRunner (Simulation)	5	5	0	100%
✅ Overall Testing Success Rate: 100%

Advantages of Using Postman and WinRunner:
Advantage	Explanation
Automation Support	Reduces manual testing time.
Accurate Validation	Validates responses and UI elements precisely.
Reusability	Test scripts can be reused for regression testing.
Error Detection	Detects logic, performance, and data-related issues early.
Enhanced Productivity	Increases tester efficiency through automation.

Conclusion:
The study and simulation of Postman and WinRunner testing tools on the Student Result Analyzer project clearly demonstrate the effectiveness of automation in both API-level and UI-level testing.
Postman efficiently tested backend endpoints for correct responses and data integrity, while WinRunner’s simulated functionality verified the correctness of user interactions and graphical outputs.
By integrating these tools into the testing workflow, the Student Result Analyzer project achieved comprehensive coverage, improved quality assurance, and faster validation cycles.
Hence, Postman and WinRunner serve as valuable assets in the modern software testing ecosystem, enhancing both accuracy and efficiency in web application testing.

""")