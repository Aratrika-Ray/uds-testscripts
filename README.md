# UshurDocumentService unit test
File description
	- MQ interface classes : 
		- Producer.py : Class to connect to the Unit test(mocks UEN)-UDS queue and send 			   transformation request message from the unit test case to UDS.
		- Consumer.py : Class to connect to the UDS-Unit test(mocks UEN) queue and receive 				  transformation response from UDS.
	- Utility classes : 
		- RabbitMQConfiguration.py : This class will read the configurations from the uds.yml file 				  of the parent UDS process.
		- RabbitMQUtility.py : This utility class esthablishes MQ connection between UDS and the 				Unit test script.
		- RequestMessage.py : This class is responsible for generating the request message using the 				RequestMessageTemplate.json file.
		- S3Utility.py : Utility class for uploading the asset to be transformed and downloading the 				transformed asset from the configured S3 bucket.
	- Template classes : 
		- RequestMessageTemplate.json : The template for the Unit test (nocks UEN) to UDS request 				 message.
	- Executable class : 
		- UDSTest.py : Entry point for the unit test case. For running the class the below command 				 should be executed.
					   python UDSTest.py

# What is the regression suite?
The regression test suite automates the otherwise manual process of cross checking transformed and expected files. UDS developers can catch regression issues by running it before every code commit. As of yet, 21 test cases have been covered out of 22.<br/>
The regression test suite works in 2 sections - first by transforming the files using the old classifier rules and then using the new classifier (NeuralNetClassifier) rules. To distinguish between the different transformations, the folders are named as Unit_Test_(number) and NeuralNetClassifier_Unit_Test_(number).

# How to run the regression suite?
Before running the regression suite -
1. move into this folder - /opt/jdk-11.0.2/lib/security/
2. run this command - keytool -import -alias infoquerycert 'path_to_UshurDocumentService/testscripts/cert.pem' -file -keystore /opt/jdk-11.0.2/lib/security/cacerts
<br/>
<li>To see everything on the screen - python3 SetUDSTest.py RegressionTests/</li>
<li>If you plan on closing the terminal session after a while use - nohup python3 SetUDSTest.py RegressionTests/ > regression_report.txt &</li>
<li>To run a single test case use - python3 SetUDSTest.py RegressionTests/Unit_Test_(number) OR nohup python3 SetUDSTest.py RegressionTests/Unit_Test_(number) &</li>
<br/>
<b>Where can you check the output of the RegressionSuite?</b><br/>
You can check the result of the RegressionSuite in regression_report_(date_of_regressionsuite_execution).txt (eg: regression_report_2022-02-02.txt) as well as nohup.out
<br/>
<b>What is RegressionTests?</b>
<br/>RegressionTests is a folder that contains all the Unit Test folders. Each unit test folder contains the original file(s), the expected file(s), the request message template files(s) and the transformed file(s)

# To learn more:
https://docs.google.com/document/d/1pdxoX5UqSGAOca0PydXJ6B6v7IlRQ0E2JXais1PyfUc/edit?usp=sharing
