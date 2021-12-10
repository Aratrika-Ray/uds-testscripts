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
	