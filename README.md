# Melbourne House Price 

## Table of Contents

1. [Overview](#overview)


## Overview <a name="overview"></a>

DISCLAIMER: this project make use of a web scrapper, and thus this project is for educational purpose only!

The purpose of this project is to collect Melbourne house price data from auction results which are published weekly by [Domain](https://www.domain.com.au/auction-results/melbourne).


## Architecture

[diagram](assets/melbourne_house_price.jpg)

The flow of the data collection starts from `CloudWatch Event` which is triggered weekly to call a `Python Lambda function` to scrap and collect auction data, do some data cleaning and store it in `RDS Postgres database`.

User can then view the data by making a request to S3 to open a React frontend which will display the latest auction data.

