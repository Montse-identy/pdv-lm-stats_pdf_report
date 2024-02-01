# https://github.com/Touchless-ID/pdv-lm-stats_pdf_report

## Project Overview

This repository contains the source code and assets for generating reports based on product metadata extracted from LM.
It is organized into different folders to help keep things organized and make it easier to navigate.

## Folder Structure

Here is an overview of the main folders and their purposes:

- **/src**: This folder contains all the source code for the project. You'll find a DEV and a PROD folder. PROD is the code in use. DEV is some tests done with Dash.

- **/data**: This folder stores sample data files required for the project. Mainly some .csv for testing.

- **/assets**: Store static assets needed for the Dash tests.

## Getting Started

To get started with the project, follow these steps:

1. Clone the repository to your local machine.
2. Navigate to the `/src` folder to find the project's main code.

Note this folder structure is tested for PROD src code. DEV code could complain of file structure, as repo was organized after the Dash POC.

## Commands to generate image and upload it to AWS

docker build --platform linux/amd64 -t lm_basic_report_ocr .
docker tag lm_basic_report_ocr:latest 967675061424.dkr.ecr.us-east-1.amazonaws.com/lm_basic_report_ocr:latest
docker push 967675061424.dkr.ecr.us-east-1.amazonaws.com/lm_basic_report_ocr:latest

## AWS resources

 Lambda function: https://us-east-1.console.aws.amazon.com/lambda/home?region=us-east-1#/functions/LM_OCR_Basic_PDF_Report?code&tab=code