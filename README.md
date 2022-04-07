# pricefx-api

  

This repo contains reusable python code for interacting with the PFX API. The included script will extract data and load into an mssql table. 

>Note: Authentication for this repo is using dedicated PFX user credentials in both prod/non-prod. PFX also offers API key authentication that may better suit our needs in the future. 

[PFX API docs here](https://qa.pricefx.eu/pricefx-api/)

## Config File
Template added to this repo for simplicity, however please consider using a secret manager or other more secure method for sensitive credentials. We use keyring locally and secret manager in the cloud. 

## Request body

Including a body in your request: you can include a body in your api request if you wish to extract only filtered data. Your json body should look something like this:

	body  = {
			    "startRow": 0,
			    "endRow": 300,
			    "sortBy": ["-attribute8"],
			    "textMatchStyle": "substring",
				"operationType": "fetch",
				"data": {
					    "_constructor": "AdvancedCriteria",
					    "operator": "and",
					    "criteria": [
							{
							    "fieldName": "attribute1",
							    "operator": "equals", 
							    "value": "text"},
							{
							    "fieldName": "attribute2",
							    "operator": "notEqual", 
							    "value": "text"},
						    {
							    "fieldName": "attribute7",
							    "operator": "notInSet",
							    "value": ["value", "value"]},
						]
    
			    }
    }