FORMAT: 1A
HOST: https://api.usaspending.gov

# List Program Activities [/api/v2/agency/{toptier_code}/program_activity/{?fiscal_year,filter,order,sort,page,limit}]

Returns a list of Program Activity in the Agency's appropriations for a single fiscal year

## GET

+ Request (application/json)
    + Schema

            {
                "$schema": "http://json-schema.org/draft-04/schema#",
                "type": "number"
            }
    + Parameters
        + `toptier_code`: 086 (required, number)
            The toptier code of an agency (could be a CGAG or FREC) so only numeric character strings of length 3-4 are accepted.
        + `fiscal_year` (optional, number)
            The desired appropriations fiscal year. Defaults to the current FY.
        + `filter` (optional, string)
            This will filter the Program Activity by their name to those matching the text.
        + `order` (optional, enum[string])
            Indicates what direction results should be sorted by. Valid options include asc for ascending order or desc for descending order.
            + Default: `desc`
            + Members
                + `desc`
                + `asc`
        + `sort` (optional, enum[string])
            Optional parameter indicating what value results should be sorted by.
            + Default: `obligated_amount`
            + Members
                + `name`
                + `obligated_amount`
                + `gross_outlay_amount`
        + `page` (optional, number)
            The page number that is currently returned.
            + Default: 1
        + `limit` (optional, number)
            How many results are returned.
            + Default: 10

+ Response 200 (application/json)
    + Attributes
        + `toptier_code` (required, string)
        + `fiscal_year` (required, number)
        + `limit` (required, number)
        + `page_metadata` (required, PageMetadata, fixed-type)
            Information used for pagination of results.
        + `results` (required, array[ProgramActivity], fixed-type)
        + `messages` (required, array[string])
            An array of warnings or instructional directives to aid consumers of this endpoint with development and debugging.

    + Body

            {
                "toptier_code": "086",
                "fiscal_year": 2018,
                "limit": 2,
                "page_metadata": {
                    "page": 1,
                    "next": 2,
                    "previous": null,
                    "hasNext": true,
                    "hasPrevious": false
                },
                "results": [
                    {
                        "name": "TI INFORMATION TECHNOLOGY",
                        "obligated_amount": 18482.4,
                        "gross_outlay_amount": -236601.1
                    },
                    {
                        "name": "CONTRACT RENEWALS",
                        "obligated_amount": 225.26,
                        "gross_outlay_amount": -161252.0
                    }
                ],
                "messages": []
            }

# Data Structures

## ProgramActivity (object)
+ `name` (required, string)
+ `obligated_amount` (required, number)
+ `gross_outlay_amount` (required, number)

## PageMetadata (object)
+ `page` (required, number)
+ `next` (optional, number)
+ `previous` (optional, number)
+ `hasNext` (required, boolean)
+ `hasPrevious` (required, boolean)
